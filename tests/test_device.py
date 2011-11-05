# -*- coding: utf-8 -*-
# Copyright (C) 2010, 2011 Sebastian Wiesner <lunaryorn@googlemail.com>

# This library is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation; either version 2.1 of the License, or (at your
# option) any later version.

# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA


from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import re
import os
import stat
import operator
import sys
import gc
from itertools import count
from datetime import timedelta

import pytest
import mock

from pyudev import (Device,
                    DeviceNotFoundAtPathError,
                    DeviceNotFoundByNameError,
                    DeviceNotFoundByNumberError,
                    DeviceNotFoundInEnvironmentError)
from pyudev.device import Attributes, Tags


def pytest_generate_tests(metafunc):
    args = metafunc.funcargnames
    if any(a in ('sys_path', 'device_path', 'device') for a in args):
        devices = pytest.get_device_sample(metafunc.config)
        for device_path in devices:
            metafunc.addcall(id=device_path, param=device_path)
    elif 'operator' in args:
        for op in (operator.gt, operator.lt, operator.le, operator.ge):
            metafunc.addcall(funcargs=dict(operator=op), id=op.__name__)


class TestDevice(object):

    def test_from_path(self, context, device_path, sys_path):
        device = Device.from_path(context, device_path)
        assert device is not None
        assert device == Device.from_sys_path(context, sys_path)
        assert device == Device.from_path(context, sys_path)

    def test_from_path_strips_leading_slash(self, context):
        assert Device.from_path(context, 'devices/platform') == \
               Device.from_path(context, '/devices/platform')

    def test_from_sys_path(self, context, sys_path):
        device = Device.from_sys_path(context, sys_path)
        assert device is not None
        assert device.sys_path == sys_path

    def test_from_sys_path_device_not_found(self, context):
        sys_path = 'there_will_not_be_such_a_device'
        with pytest.raises(DeviceNotFoundAtPathError) as exc_info:
            Device.from_sys_path(context, sys_path)
        error = exc_info.value
        assert error.sys_path == sys_path
        assert str(error) == 'No device at {0!r}'.format(sys_path)

    def test_from_name(self, context, device):
        new_device = Device.from_name(context, device.subsystem,
                                      device.sys_name)
        assert new_device == device

    def test_from_name_no_device_in_existing_subsystem(self, context):
        with pytest.raises(DeviceNotFoundByNameError) as exc_info:
            Device.from_name(context, 'block', 'foobar')
        error = exc_info.value
        assert error.subsystem == 'block'
        assert error.sys_name == 'foobar'
        assert str(error) == 'No device {0!r} in {1!r}'.format(
            error.sys_name, error.subsystem)

    def test_from_name_nonexisting_subsystem(self, context):
        with pytest.raises(DeviceNotFoundByNameError) as exc_info:
            Device.from_name(context, 'no_such_subsystem', 'foobar')
        error = exc_info.value
        assert error.subsystem == 'no_such_subsystem'
        assert error.sys_name == 'foobar'
        assert str(error) == 'No device {0!r} in {1!r}'.format(
            error.sys_name, error.subsystem)

    def test_from_device_number(self, context, device_path, device_number,
                                device_node):
        if not device_node:
            pytest.skip('no device node, no device number')
        mode = os.stat(device_node).st_mode
        type = 'block' if stat.S_ISBLK(mode) else 'char'
        device = Device.from_device_number(context, type, device_number)
        assert device.device_number == device_number
        # make sure, we are really referring to the same device
        assert device.device_path == device_path

    def test_from_device_number_wrong_type(self, context, device_path,
                                           device_number, device_node):
        if not device_node:
            pytest.skip('no device node, no device number')
        mode = os.stat(device_node).st_mode
        # deliberately use the wrong type here to cause either failure or at
        # least device mismatch
        type = 'char' if stat.S_ISBLK(mode) else 'block'
        try:
            # this either fails, in which case the caught exception is raised,
            # or succeeds, but returns a wrong device (device numbers are not
            # unique across device types)
            device = Device.from_device_number(context, type, device_number)
            # if it succeeds, the resulting device must not match the one, we
            # are actually looking for!
            assert device.device_path != device_path
        except DeviceNotFoundByNumberError as error:
            # check the correctness of the exception attributes
            assert error.device_type == type
            assert error.device_number == device_number

    def test_from_device_number_invalid_type(self, context):
        with pytest.raises(ValueError) as exc_info:
            Device.from_device_number(context, 'foobar', 100)
        assert str(exc_info.value) == ('Invalid type: {0!r}. Must be one of '
                                       '"char" or "block".'.format('foobar'))

    @pytest.need_udev_version('>= 152')
    def test_from_environment(self, context):
        # there is no device in a standard environment
        with pytest.raises(DeviceNotFoundInEnvironmentError):
            Device.from_environment(context)

    def test_parent(self, device):
        assert device.parent is None or isinstance(device.parent, Device)

    @pytest.need_udev_version('>= 172')
    def test_child_of_parent(self, device):
        if device.parent is None:
            pytest.skip('Device {0!r} has no parent'.format(device))
        else:
            assert device in device.parent.children

    @pytest.need_udev_version('>= 172')
    def test_children(self, device):
        children = list(device.children)
        if not children:
            pytest.skip('Device {0!r} has no children'.format(device))
        else:
            assert all(c != device for c in children)
            assert all(c.parent == device for c in children)

    def test_find_parent(self, device):
        parent = device.find_parent(device.subsystem)
        if not parent:
            pytest.xfail('no parent within the same subsystem')
        assert parent.subsystem == device.subsystem
        assert parent in device.traverse()

    def test_find_parent_no_devtype_mock(self, device):
        get_parent = 'udev_device_get_parent_with_subsystem_devtype'
        ref = 'udev_device_ref'
        with pytest.nested(pytest.patch_libudev(get_parent),
                           pytest.patch_libudev(ref)) as (get_parent, ref):
            get_parent.return_value = mock.sentinel.device
            ref.return_value = mock.sentinel.referenced_device
            parent = device.find_parent('subsystem')
            get_parent.assert_called_with(device, b'subsystem', None)
            ref.assert_called_with(mock.sentinel.device)
            assert isinstance(get_parent.call_args[0][1], bytes)
            assert isinstance(parent, Device)
            assert parent._as_parameter_ is mock.sentinel.referenced_device

    def test_find_parent_with_devtype_mock(self, device):
        get_parent = 'udev_device_get_parent_with_subsystem_devtype'
        ref = 'udev_device_ref'
        with pytest.nested(pytest.patch_libudev(get_parent),
                           pytest.patch_libudev(ref)) as (get_parent, ref):
            get_parent.return_value = mock.sentinel.device
            ref.return_value = mock.sentinel.referenced_device
            parent = device.find_parent('subsystem', 'devtype')
            get_parent.assert_called_with(device, b'subsystem', b'devtype')
            ref.assert_called_with(mock.sentinel.device)
            args = get_parent.call_args[0][1:]
            assert all(isinstance(a, bytes) for a in args)
            assert isinstance(parent, Device)
            assert parent._as_parameter_ is mock.sentinel.referenced_device

    def test_traverse(self, device):
        child = device
        for parent in device.traverse():
            assert parent == child.parent
            child = parent

    def test_sys_path(self, device, sys_path):
        assert device.sys_path == sys_path
        assert pytest.is_unicode_string(device.sys_path)

    def test_device_path(self, device, device_path):
        assert device.device_path == device_path
        assert pytest.is_unicode_string(device.device_path)

    def test_subsystem(self, device, properties):
        assert device.subsystem == properties['SUBSYSTEM']
        assert pytest.is_unicode_string(device.subsystem)

    def test_device_sys_name(self, device):
        assert device.sys_name == os.path.basename(device.device_path)
        assert pytest.is_unicode_string(device.sys_name)

    def test_sys_number(self, device):
        match = re.search(r'\d+$', device.sys_name)
        # filter out devices with completely nummeric names (first character
        # doesn't count according to the implementation of libudev)
        if match and match.start() > 1:
            assert device.sys_number == match.group(0)
            assert pytest.is_unicode_string(device.sys_name)
        else:
            assert device.sys_number is None

    def test_type(self, device, properties):
        if 'DEVTYPE' in properties:
            assert device.device_type == properties['DEVTYPE']
            assert pytest.is_unicode_string(device.device_type)
        else:
            assert device.device_type is None

    def test_driver(self, device, properties):
        if 'DRIVER' in properties:
            assert device.driver == properties['DRIVER']
            assert pytest.is_unicode_string(device.driver)
        else:
            assert device.driver is None

    def test_device_node(self, device, device_node):
        if device_node:
            assert device.device_node == device_node
            assert pytest.is_unicode_string(device.device_node)
        else:
            assert device.device_node is None

    def test_device_number(self, device, device_number):
        assert device.device_number == device_number

    @pytest.need_udev_version('>= 165')
    def test_is_initialized(self, device):
        assert isinstance(device.is_initialized, bool)
        get_is_initialized = 'udev_device_get_is_initialized'
        with pytest.patch_libudev(get_is_initialized) as get_is_initialized:
            get_is_initialized.return_value = True
            assert device.is_initialized
            get_is_initialized.assert_called_with(device)

    @pytest.need_udev_version('>= 165')
    def test_time_since_initialized(self, device):
        assert isinstance(device.time_since_initialized, timedelta)
        usec_since_init = 'udev_device_get_usec_since_initialized'
        with pytest.patch_libudev(usec_since_init) as usec_since_init:
            usec_since_init.return_value = 100
            assert device.time_since_initialized.microseconds == 100
            usec_since_init.assert_called_with(device)

    def test_links(self, context, device, device_links):
        assert sorted(device.device_links) == sorted(
            os.path.join(context.device_path, l) for l in device_links)
        assert all(pytest.is_unicode_string(l) for l in device.device_links)

    def test_attributes(self, device):
        # see TestAttributes for complete attribute tests
        assert isinstance(device.attributes, Attributes)

    def test_no_leak(self, context):
        """
        Regression test for issue #32, modelled after the script which revealed
        this issue.

        The leak was caused by the following reference cycle between
        ``Attributes`` and ``Device``:

        Device._attributes -> Attributes.device

        https://github.com/lunaryorn/pyudev/issues/32
        """
        for _ in context.list_devices(subsystem='usb'):
            pass
        # make sure that no memory leaks
        assert not gc.garbage

    def test_tags(self, device):
        # see TestTags for complete tag tests
        assert isinstance(device.tags, Tags)

    def test_iteration(self, device, properties):
        device_properties = set(device)
        assert all(p in device_properties for p in properties)
        assert all(pytest.is_unicode_string(p) for p in device_properties)

    def test_length(self, device, all_properties):
        assert len(device) == len(all_properties)

    def test_getitem(self, device, properties):
        assert all(device[p] == properties[p] for p in properties)

    def test_getitem_devname(self, context, device, all_properties):
        if 'DEVNAME' not in all_properties:
            pytest.xfail('%r has no DEVNAME' % device)
        assert os.path.join(context.device_path, device['DEVNAME']) == \
               os.path.join(context.device_path, all_properties['DEVNAME'])

    def test_getitem_nonexisting(self, device):
        with pytest.raises(KeyError) as excinfo:
            device['a non-existing property']
        assert str(excinfo.value) == repr('a non-existing property')

    def test_asint(self, device, properties):
        for property in properties:
            value = properties[property]
            try:
                value = int(value)
            except ValueError:
                with pytest.raises(ValueError):
                    device.asint(property)
            else:
                assert device.asint(property) == value

    def test_asbool(self, device, properties):
        for property in properties:
            value = properties[property]
            if value == '1':
                assert device.asbool(property)
            elif value == '0':
                assert not device.asbool(property)
            else:
                with pytest.raises(ValueError) as exc_info:
                    device.asbool(property)
                message = 'Not a boolean value: {0!r}'
                assert str(exc_info.value) == message.format(value)

    def test_hash(self, device):
        assert hash(device) == hash(device.device_path)
        assert hash(device.parent) == hash(device.parent)
        assert hash(device.parent) != hash(device)

    def test_equality(self, device):
        assert device == device.device_path
        assert device == device
        assert device.parent == device.parent
        assert not (device == device.parent)

    def test_inequality(self, device):
        assert not (device != device.device_path)
        assert not (device != device)
        assert not (device.parent != device.parent)
        assert device != device.parent

    def test_device_ordering(self, platform_device, operator):
        with pytest.raises(TypeError) as exc_info:
            operator(platform_device, platform_device)
        assert str(exc_info.value) == 'Device not orderable'


class TestAttributes(object):

    def test_length(self, device):
        counter = count()
        for _ in device.attributes:
            next(counter)
        assert len(device.attributes) == next(counter)

    def test_iteration(self, device, attributes):
        device_attributes = set(device.attributes)
        assert all(a in device_attributes for a in attributes)
        assert all(pytest.is_unicode_string(a) for a in device_attributes)

    @pytest.need_udev_version('>= 167')
    def test_iteration_mock(self, device):
        attributes = [b'spam', b'eggs']
        get_sysattr_list = 'udev_device_get_sysattr_list_entry'
        with pytest.patch_libudev_list(attributes,
                                       get_sysattr_list) as get_sysattr_list:
            attrs = list(device.attributes)
            assert attrs == ['spam', 'eggs']
            get_sysattr_list.assert_called_with(device)

    def test_contains(self, device, attributes):
        assert all(a in device.attributes for a in attributes)

    def test_getitem(self, device, attributes):
        assert all(isinstance(device.attributes[a], bytes) for a in attributes)
        assert all(device.attributes[a] == v.encode(sys.getfilesystemencoding())
                   for a, v in attributes.items())

    def test_getitem_nonexisting(self, device):
        with pytest.raises(KeyError) as excinfo:
            device.attributes['a non-existing attribute']
        print(type(excinfo.value))
        assert str(excinfo.value) == repr('a non-existing attribute')

    def test_asstring(self, device, attributes):
        assert all(pytest.is_unicode_string(device.attributes.asstring(a))
                   for a in attributes)
        assert all(device.attributes.asstring(a) == v
                   for a, v in attributes.items())

    def test_asint(self, device, attributes):
        for attribute, value in attributes.items():
            try:
                value = int(value)
            except ValueError:
                with pytest.raises(ValueError):
                    device.attributes.asint(attribute)
            else:
                assert device.attributes.asint(attribute) == value

    def test_asbool(self, device, attributes):
        for attribute, value in attributes.items():
            if value == '1':
                assert device.attributes.asbool(attribute)
            elif value == '0':
                assert not device.attributes.asbool(attribute)
            else:
                with pytest.raises(ValueError) as exc_info:
                    device.attributes.asbool(attribute)
                message = 'Not a boolean value: {0!r}'
                assert str(exc_info.value) == message.format(value)


class TestTags(object):

    pytestmark = pytest.need_udev_version('>= 154')

    def test_iteration(self, device, tags):
        assert set(device.tags) == set(tags)
        assert all(pytest.is_unicode_string(t) for t in device.tags)

    def test_contains(self, device, tags):
        assert all(t in device.tags for t in tags)

    @pytest.need_udev_version('>= 172')
    def test_contains_mock(self, device):
        """
        Test that ``udev_device_has_tag`` is called if available.
        """
        has_tag = 'udev_device_has_tag'
        with pytest.patch_libudev(has_tag) as has_tag:
            has_tag.return_value = 1
            assert 'foo' in device.tags
            has_tag.assert_called_with(device, b'foo')
