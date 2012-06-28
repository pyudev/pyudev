# -*- coding: utf-8 -*-
# Copyright (C) 2010, 2011, 2012 Sebastian Wiesner <lunaryorn@gmail.com>

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
import errno
from itertools import count
from datetime import timedelta

import pytest
from mock import sentinel

from pyudev import (Device,
                    DeviceNotFoundAtPathError,
                    DeviceNotFoundByNameError,
                    DeviceNotFoundByNumberError,
                    DeviceNotFoundInEnvironmentError)
from pyudev.device import Attributes, Tags
from pyudev._libudev import libudev


with_device_data = pytest.mark.parametrize(
    'device_data', pytest.config.udev_device_sample,
    ids=pytest.config.udev_device_sample)


with_devices = pytest.mark.parametrize(
    'device', pytest.config.udev_device_sample,
    indirect=True, ids=pytest.config.udev_device_sample)


def pytest_funcarg__device(request):
    device_data = getattr(request, 'param', None) or \
                  request.getfuncargvalue('device_data')
    context = request.getfuncargvalue('context')
    return Device.from_path(context, device_data.device_path)


class TestDevice(object):

    @with_device_data
    def test_from_path(self, context, device_data):
        device = Device.from_path(context, device_data.device_path)
        assert device is not None
        assert device == Device.from_sys_path(context, device_data.sys_path)
        assert device == Device.from_path(context, device_data.sys_path)

    def test_from_path_strips_leading_slash(self, context):
        assert Device.from_path(context, 'devices/platform') == \
               Device.from_path(context, '/devices/platform')

    @with_device_data
    def test_from_sys_path(self, context, device_data):
        device = Device.from_sys_path(context, device_data.sys_path)
        assert device is not None
        assert device.sys_path == device_data.sys_path

    def test_from_sys_path_device_not_found(self, context):
        sys_path = 'there_will_not_be_such_a_device'
        with pytest.raises(DeviceNotFoundAtPathError) as exc_info:
            Device.from_sys_path(context, sys_path)
        error = exc_info.value
        assert error.sys_path == sys_path
        assert str(error) == 'No device at {0!r}'.format(sys_path)

    @with_devices
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

    @with_device_data
    def test_from_device_number(self, context, device_data):
        if not device_data.device_node:
            pytest.skip('no device node, no device number')
        mode = os.stat(device_data.device_node).st_mode
        type = 'block' if stat.S_ISBLK(mode) else 'char'
        device = Device.from_device_number(
            context, type, device_data.device_number)
        assert device.device_number == device_data.device_number
        # make sure, we are really referring to the same device
        assert device.device_path == device_data.device_path

    @with_device_data
    def test_from_device_number_wrong_type(self, context, device_data):
        if not device_data.device_node:
            pytest.skip('no device node, no device number')
        mode = os.stat(device_data.device_node).st_mode
        # deliberately use the wrong type here to cause either failure or at
        # least device mismatch
        type = 'char' if stat.S_ISBLK(mode) else 'block'
        try:
            # this either fails, in which case the caught exception is raised,
            # or succeeds, but returns a wrong device (device numbers are not
            # unique across device types)
            device = Device.from_device_number(
                context, type, device_data.device_number)
            # if it succeeds, the resulting device must not match the one, we
            # are actually looking for!
            assert device.device_path != device_data.device_path
        except DeviceNotFoundByNumberError as error:
            # check the correctness of the exception attributes
            assert error.device_type == type
            assert error.device_number == device_data.device_number

    def test_from_device_number_invalid_type(self, context):
        with pytest.raises(ValueError) as exc_info:
            Device.from_device_number(context, 'foobar', 100)
        assert str(exc_info.value) == ('Invalid type: {0!r}. Must be one of '
                                       '"char" or "block".'.format('foobar'))

    @with_device_data
    def test_from_device_file(self, context, device_data):
        if not device_data.device_node:
            pytest.skip('no device file')
        device = Device.from_device_file(context, device_data.device_node)
        assert device.device_node == device_data.device_node
        assert device.device_path == device_data.device_path

    @with_device_data
    def test_from_device_file_links(self, context, device_data):
        if not device_data.device_links:
            pytest.skip('no device links')
        for link in device_data.device_links:
            link = os.path.join(context.device_path, link)
            device = Device.from_device_file(context, link)
            assert device.device_path == device_data.device_path
            assert link in device.device_links

    def test_from_device_file_no_device_file(self, context, tmpdir):
        filename = tmpdir.join('test')
        filename.ensure(file=True)
        with pytest.raises(ValueError) as excinfo:
            Device.from_device_file(context, str(filename))
        message = 'not a device file: {0!r}'.format(str(filename))
        assert str(excinfo.value) == message

    def test_from_device_file_non_existing(self, context, tmpdir):
        filename = tmpdir.join('test')
        assert not tmpdir.check(file=True)
        with pytest.raises(EnvironmentError) as excinfo:
            Device.from_device_file(context, str(filename))
        pytest.assert_env_error(excinfo.value, errno.ENOENT, str(filename))

    @pytest.mark.udev_version('>= 152')
    def test_from_environment(self, context):
        # there is no device in a standard environment
        with pytest.raises(DeviceNotFoundInEnvironmentError):
            Device.from_environment(context)

    @with_devices
    def test_parent(self, device):
        assert device.parent is None or isinstance(device.parent, Device)

    @pytest.mark.udev_version('>= 172')
    @with_devices
    def test_child_of_parent(self, device):
        if device.parent is None:
            pytest.skip('Device {0!r} has no parent'.format(device))
        else:
            assert device in device.parent.children

    @pytest.mark.udev_version('>= 172')
    @with_devices
    def test_children(self, device):
        children = list(device.children)
        if not children:
            pytest.skip('Device {0!r} has no children'.format(device))
        else:
            for child in children:
                assert child != device
                assert device in child.ancestors

    @with_devices
    def test_ancestors(self, device):
        child = device
        for ancestor in device.ancestors:
            assert ancestor == child.parent
            child = ancestor

    @with_devices
    def test_find_parent(self, device):
        parent = device.find_parent(device.subsystem)
        if not parent:
            pytest.skip('no parent within the same subsystem')
        assert parent.subsystem == device.subsystem
        assert parent in device.ancestors

    @with_devices
    def test_find_parent_no_devtype_mock(self, device):
        calls = {'udev_device_get_parent_with_subsystem_devtype':
                 [(device, b'subsystem', None)],
                 'udev_device_ref': [(sentinel.parent_device,)]}
        with pytest.calls_to_libudev(calls):
            f = libudev.udev_device_get_parent_with_subsystem_devtype
            f.return_value = sentinel.parent_device
            libudev.udev_device_ref.return_value = sentinel.ref_device
            parent = device.find_parent('subsystem')
            assert isinstance(parent, Device)
            assert parent._as_parameter_ is sentinel.ref_device

    @with_devices
    def test_find_parent_with_devtype_mock(self, device):
        calls = {'udev_device_get_parent_with_subsystem_devtype':
                 [(device, b'subsystem', b'devtype')],
                 'udev_device_ref': [(sentinel.parent_device,)]}
        with pytest.calls_to_libudev(calls):
            f = libudev.udev_device_get_parent_with_subsystem_devtype
            f.return_value = sentinel.parent_device
            libudev.udev_device_ref.return_value = sentinel.ref_device
            parent = device.find_parent('subsystem', 'devtype')
            assert isinstance(parent, Device)
            assert parent._as_parameter_ is sentinel.ref_device

    @with_devices
    def test_traverse(self, device):
        child = device
        for parent in pytest.deprecated_call(device.traverse):
            assert parent == child.parent
            child = parent

    @with_device_data
    def test_sys_path(self, device, device_data):
        assert device.sys_path == device_data.sys_path
        assert pytest.is_unicode_string(device.sys_path)

    @with_device_data
    def test_device_path(self, device, device_data):
        assert device.device_path == device_data.device_path
        assert pytest.is_unicode_string(device.device_path)

    @with_device_data
    def test_subsystem(self, device, device_data):
        assert device.subsystem == device_data.properties['SUBSYSTEM']
        assert pytest.is_unicode_string(device.subsystem)

    @with_devices
    def test_device_sys_name(self, device):
        assert device.sys_name == os.path.basename(device.device_path)
        assert pytest.is_unicode_string(device.sys_name)

    @with_devices
    def test_sys_number(self, device):
        match = re.search(r'\d+$', device.sys_name)
        # filter out devices with completely nummeric names (first character
        # doesn't count according to the implementation of libudev)
        if match and match.start() > 1:
            assert device.sys_number == match.group(0)
            assert pytest.is_unicode_string(device.sys_name)
        else:
            assert device.sys_number is None

    @with_device_data
    def test_type(self, device, device_data):
        assert device.device_type == device_data.properties.get('DEVTYPE')
        if device.device_type:
            assert pytest.is_unicode_string(device.device_type)

    @with_device_data
    def test_driver(self, device, device_data):
        assert device.driver == device_data.properties.get('DRIVER')
        if device.driver:
            assert pytest.is_unicode_string(device.driver)

    @with_device_data
    def test_device_node(self, device, device_data):
        assert device.device_node == device_data.device_node
        if device.device_node:
            assert pytest.is_unicode_string(device.device_node)

    @with_device_data
    def test_device_number(self, device, device_data):
        assert device.device_number == device_data.device_number

    @pytest.mark.udev_version('>= 165')
    @with_devices
    def test_is_initialized(self, device):
        assert isinstance(device.is_initialized, bool)

    @pytest.mark.udev_version('>= 165')
    @with_devices
    def test_is_initialized_mock(self, device):
        calls = {'udev_device_get_is_initialized': [(device,)]}
        with pytest.calls_to_libudev(calls):
            libudev.udev_device_get_is_initialized.return_value = False
            assert not device.is_initialized

    @pytest.mark.udev_version('>= 165')
    @with_devices
    def test_time_since_initialized(self, device):
        assert isinstance(device.time_since_initialized, timedelta)

    @pytest.mark.udev_version('>= 165')
    @with_devices
    def test_time_since_initialized_mock(self, device):
        calls = {'udev_device_get_usec_since_initialized': [(device,)]}
        with pytest.calls_to_libudev(calls):
            libudev.udev_device_get_usec_since_initialized.return_value = 100
            assert device.time_since_initialized.microseconds == 100

    @with_device_data
    def test_links(self, context, device, device_data):
        assert sorted(device.device_links) == sorted(device_data.device_links)
        for link in device.device_links:
            assert pytest.is_unicode_string(link)

    @with_devices
    def test_action(self, device):
        assert device.action is None

    @with_devices
    def test_action_mock(self, device):
        calls = {'udev_device_get_action': [(device,)]}
        with pytest.calls_to_libudev(calls):
            libudev.udev_device_get_action.return_value = b'spam'
            assert device.action == 'spam'
            assert pytest.is_unicode_string(device.action)

    @with_devices
    @pytest.mark.seqnum
    def test_sequence_number(self, device):
        assert device.sequence_number == 0

    @with_devices
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

    @with_devices
    def test_tags(self, device):
        # see TestTags for complete tag tests
        assert isinstance(device.tags, Tags)

    @with_device_data
    def test_iteration(self, device, device_data):
        for property in device:
            assert pytest.is_unicode_string(property)
        # test that iteration really yields all properties
        device_properties = set(device)
        for property in device_data.properties:
            assert property in device_properties

    @with_device_data
    def test_length(self, device, device_data):
        assert len(device) == len(device_data.properties)

    @with_device_data
    def test_getitem(self, device, device_data):
        for property in device_data.properties:
            assert device[property] == device_data.properties[property]

    @with_device_data
    def test_getitem_devname(self, context, device, device_data):
        if 'DEVNAME' not in device_data.properties:
            pytest.skip('%r has no DEVNAME' % device)
        data_devname = os.path.join(
            context.device_path, device_data.properties['DEVNAME'])
        device_devname = os.path.join(context.device_path, device['DEVNAME'])
        assert device_devname == data_devname

    @with_devices
    def test_getitem_nonexisting(self, device):
        with pytest.raises(KeyError) as excinfo:
            device['a non-existing property']
        assert str(excinfo.value) == repr('a non-existing property')

    @with_device_data
    def test_asint(self, device, device_data):
        for property, value in device_data.properties.items():
            try:
                value = int(value)
            except ValueError:
                with pytest.raises(ValueError):
                    device.asint(property)
            else:
                assert device.asint(property) == value

    @with_device_data
    def test_asbool(self, device, device_data):
        for property, value in device_data.properties.items():
            if value == '1':
                assert device.asbool(property)
            elif value == '0':
                assert not device.asbool(property)
            else:
                with pytest.raises(ValueError) as exc_info:
                    device.asbool(property)
                message = 'Not a boolean value: {0!r}'
                assert str(exc_info.value) == message.format(value)

    @with_devices
    def test_hash(self, device):
        assert hash(device) == hash(device.device_path)
        assert hash(device.parent) == hash(device.parent)
        assert hash(device.parent) != hash(device)

    @with_devices
    def test_equality(self, device):
        assert device == device.device_path
        assert device == device
        assert device.parent == device.parent
        assert not (device == device.parent)

    @with_devices
    def test_inequality(self, device):
        assert not (device != device.device_path)
        assert not (device != device)
        assert not (device.parent != device.parent)
        assert device != device.parent

    ORDERING_OPERATORS = [operator.gt, operator.lt, operator.le, operator.ge]

    @pytest.mark.parametrize(
        'operator', ORDERING_OPERATORS,
        ids=[f.__name__ for f in ORDERING_OPERATORS])
    def test_device_ordering(self, context, operator):
        device = Device.from_path(context, '/devices/platform')
        with pytest.raises(TypeError) as exc_info:
            operator(device, device)
        assert str(exc_info.value) == 'Device not orderable'


class TestAttributes(object):

    @with_devices
    def test_length(self, device):
        counter = count()
        for _ in device.attributes:
            next(counter)
        assert len(device.attributes) == next(counter)

    @with_device_data
    def test_iteration(self, device, device_data):
        for attribute in device.attributes:
            assert pytest.is_unicode_string(attribute)
        # check that iteration really yields all attributes
        device_attributes = set(device.attributes)
        for attribute in device_data.attributes:
            assert attribute in device_attributes

    @pytest.mark.udev_version('>= 167')
    @with_devices
    def test_iteration_mock(self, device):
        attributes = [b'spam', b'eggs']
        get_sysattr_list = 'udev_device_get_sysattr_list_entry'
        with pytest.libudev_list(get_sysattr_list, attributes):
            attrs = list(device.attributes)
            assert attrs == ['spam', 'eggs']
            f = libudev.udev_device_get_sysattr_list_entry
            f.assert_called_with(device)

    @with_device_data
    def test_contains(self, device, device_data):
        for attribute in device_data.attributes:
            assert attribute in device.attributes

    @with_device_data
    def test_getitem(self, device, device_data):
        for attribute, value in device_data.attributes.items():
            raw_value = value.encode(sys.getfilesystemencoding())
            assert isinstance(device.attributes[attribute], bytes)
            assert device.attributes[attribute] == raw_value

    @with_devices
    def test_getitem_nonexisting(self, device):
        with pytest.raises(KeyError) as excinfo:
            device.attributes['a non-existing attribute']
        assert str(excinfo.value) == repr('a non-existing attribute')

    @with_device_data
    def test_asstring(self, device, device_data):
        for attribute, value in device_data.attributes.items():
            assert pytest.is_unicode_string(
                device.attributes.asstring(attribute))
            assert device.attributes.asstring(attribute) == value

    @with_device_data
    def test_asint(self, device, device_data):
        for attribute, value in device_data.attributes.items():
            try:
                value = int(value)
            except ValueError:
                with pytest.raises(ValueError):
                    device.attributes.asint(attribute)
            else:
                assert device.attributes.asint(attribute) == value

    @with_device_data
    def test_asbool(self, device, device_data):
        for attribute, value in device_data.attributes.items():
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

    pytestmark = pytest.mark.udev_version('>= 154')

    @with_device_data
    def test_iteration(self, device, device_data):
        if not device_data.tags:
            pytest.skip('no tags on device')
        assert set(device.tags) == set(device_data.tags)
        for tag in device.tags:
            assert pytest.is_unicode_string(tag)

    @with_devices
    def test_iteration_mock(self, device):
        with pytest.libudev_list('udev_device_get_tags_list_entry',
                                 [b'spam', b'eggs']):
            tags = list(device.tags)
            assert tags == ['spam', 'eggs']
            f = libudev.udev_device_get_tags_list_entry
            f.assert_called_with(device)

    @with_device_data
    def test_contains(self, device, device_data):
        if not device_data.tags:
            pytest.skip('no tags on device')
        for tag in device_data.tags:
            assert tag in device.tags

    @pytest.mark.udev_version('>= 172')
    @with_devices
    def test_contains_mock(self, device):
        """
        Test that ``udev_device_has_tag`` is called if available.
        """
        calls = {'udev_device_has_tag': [(device, b'foo')]}
        with pytest.calls_to_libudev(calls):
            libudev.udev_device_has_tag.return_value = 1
            assert 'foo' in device.tags
