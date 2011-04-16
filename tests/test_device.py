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

import os
import operator
import sys
from itertools import count
from datetime import timedelta

import pytest
import mock

from pyudev import (Device,
                    DeviceNotFoundAtPathError,
                    DeviceNotFoundByNameError,
                    DeviceNotFoundInEnvironmentError)


def pytest_generate_tests(metafunc):
    args = metafunc.funcargnames
    if 'device_path' in args or 'device' in args:
        devices = pytest.get_device_sample(metafunc.config)
        for device_path in devices:
            metafunc.addcall(id=device_path, param=device_path)
    elif 'operator' in args:
        for op in (operator.gt, operator.lt, operator.le, operator.ge):
            metafunc.addcall(funcargs=dict(operator=op), id=op.__name__)


def test_device_from_sys_path(context, sys_path, device_path):
    device = Device.from_sys_path(context, sys_path)
    assert device is not None
    assert device.sys_path == sys_path
    assert device.device_path == device_path


def test_device_from_path(context, device_path, sys_path):
    device = Device.from_path(context, device_path)
    assert device is not None
    assert device.sys_path == sys_path
    assert device.device_path == device_path
    assert device == Device.from_sys_path(context, sys_path)
    assert device == Device.from_path(context, sys_path)


def test_device_from_path_strips_leading_slash(context):
    assert Device.from_path(context, 'devices/platform') == \
           Device.from_path(context, '/devices/platform')


def test_device_from_sys_path_device_not_found(context):
    sys_path = 'there_will_not_be_such_a_device'
    with pytest.raises(DeviceNotFoundAtPathError) as exc_info:
        Device.from_sys_path(context, sys_path)
    error = exc_info.value
    assert error.sys_path == sys_path
    assert str(error) == 'No device at {0!r}'.format(sys_path)


def test_device_from_name(context, device):
    new_device = Device.from_name(context, device.subsystem,
                                  device.sys_name)
    assert new_device == device


def test_device_from_name_no_device_in_existing_subsystem(context):
    with pytest.raises(DeviceNotFoundByNameError) as exc_info:
        Device.from_name(context, 'block', 'foobar')
    error = exc_info.value
    assert error.subsystem == 'block'
    assert error.sys_name == 'foobar'
    assert str(error) == 'No device {0!r} in {1!r}'.format(
        error.sys_name, error.subsystem)


def test_device_from_name_nonexisting_subsystem(context):
    with pytest.raises(DeviceNotFoundByNameError) as exc_info:
        Device.from_name(context, 'no_such_subsystem', 'foobar')
    error = exc_info.value
    assert error.subsystem == 'no_such_subsystem'
    assert error.sys_name == 'foobar'
    assert str(error) == 'No device {0!r} in {1!r}'.format(
        error.sys_name, error.subsystem)


@pytest.need_udev_version('>= 152')
def test_device_from_environment(context):
    # there is no device in a standard environment
    with pytest.raises(DeviceNotFoundInEnvironmentError):
        Device.from_environment(context)


@pytest.mark.properties
def test_device_properties(device, properties):
    assert all(device[p] == properties[p] for p in properties)


@pytest.mark.properties
def test_device_asint(device, properties):
    for property in properties:
        value = properties[property]
        try:
            value = int(value)
        except ValueError:
            with pytest.raises(ValueError):
                device.asint(property)
        else:
            assert device.asint(property) == value


@pytest.mark.properties
def test_device_asbool(device, properties):
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


def test_attributes_iter(device, attributes):
    device_attributes = set(device.attributes)
    assert all(a in device_attributes for a in attributes)
    assert all(pytest.is_unicode_string(a) for a in device_attributes)


def test_attributes_len(device):
    counter = count()
    for _ in device.attributes:
        next(counter)
    assert len(device.attributes) == next(counter)


def test_attributes_contains(device, attributes):
    assert all(a in device.attributes for a in attributes)


def test_attributes_getitem(device, attributes):
    assert all(isinstance(device.attributes[a], bytes) for a in attributes)
    assert all(device.attributes[a] == v.encode(sys.getfilesystemencoding())
               for a, v in attributes.items())


def test_attributes_asstring(device, attributes):
    assert all(pytest.is_unicode_string(device.attributes.asstring(a))
               for a in attributes)
    assert all(device.attributes.asstring(a) == v
               for a, v in attributes.items())


def test_attributes_asint(device, attributes):
    for attribute, value in attributes.items():
        try:
            value = int(value)
        except ValueError:
            with pytest.raises(ValueError):
                device.attributes.asint(attribute)
        else:
            assert device.attributes.asint(attribute) == value


def test_attributes_asbool(device, attributes):
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


@pytest.mark.properties
def test_device_devname(context, device, all_properties):
    if 'DEVNAME' not in all_properties:
        pytest.xfail('%r has no DEVNAME' % device)
    assert os.path.join(context.device_path, device['DEVNAME']) == \
           os.path.join(context.device_path, all_properties['DEVNAME'])


@pytest.mark.properties
def test_device_subsystem(device, properties):
    assert device.subsystem == properties['SUBSYSTEM']
    assert pytest.is_unicode_string(device.subsystem)


@pytest.mark.properties
def test_device_sys_name(device):
    assert device.sys_name == os.path.basename(device.device_path)
    assert pytest.is_unicode_string(device.sys_name)


@pytest.mark.properties
def test_device_node(context, device, device_node):
    if device_node:
        assert device.device_node == os.path.join(context.device_path,
                                                  device_node)
        assert pytest.is_unicode_string(device.device_node)
    else:
        assert device.device_node is None


@pytest.mark.properties
def test_device_links(context, device, device_links):
    assert sorted(device.device_links) == sorted(
        os.path.join(context.device_path, l) for l in device_links)
    assert all(pytest.is_unicode_string(l) for l in device.device_links)


@pytest.need_udev_version('>= 165')
@pytest.mark.properties
def test_device_is_initialized(device):
    assert isinstance(device.is_initialized, bool)
    get_is_initialized = 'udev_device_get_is_initialized'
    with pytest.patch_libudev(get_is_initialized) as get_is_initialized:
        get_is_initialized.return_value = True
        assert device.is_initialized
        get_is_initialized.assert_called_with(device)


@pytest.need_udev_version('>= 165')
@pytest.mark.properties
def test_device_time_since_initialized(device):
    assert isinstance(device.time_since_initialized, timedelta)
    usec_since_init = 'udev_device_get_usec_since_initialized'
    with pytest.patch_libudev(usec_since_init) as usec_since_init:
        usec_since_init.return_value = 100
        assert device.time_since_initialized.microseconds == 100
        usec_since_init.assert_called_with(device)


@pytest.need_udev_version('>= 154')
def test_device_tags_mock(device):
    tags_list = iter([b'spam', b'eggs', b'foo', b'bar'])

    def next_entry(entry):
        try:
            return next(tags_list)
        except StopIteration:
            return None

    def name(entry):
        if entry:
            return entry
        else:
            pytest.fail('empty entry!')

    get_tags_list_entry = 'udev_device_get_tags_list_entry'
    get_next = 'udev_list_entry_get_next'
    get_name = 'udev_list_entry_get_name'
    with pytest.nested(pytest.patch_libudev(get_tags_list_entry),
                       pytest.patch_libudev(get_name),
                       pytest.patch_libudev(get_next)) as (get_tags_list_entry,
                                                           get_name, get_next):
        get_tags_list_entry.return_value = next(tags_list)
        get_name.side_effect = name
        get_next.side_effect = next_entry

        device_tags = list(device.tags)
        assert device_tags == ['spam', 'eggs', 'foo', 'bar']
        assert all(pytest.is_unicode_string(t) for t in device_tags)


@pytest.mark.xfail(reason='Not implemented')
@pytest.need_udev_version('>= 154')
def test_device_tags():
    raise NotImplementedError()


@pytest.mark.properties
def test_device_driver(device, properties):
    if 'DRIVER' in properties:
        assert device.driver == properties['DRIVER']
        assert pytest.is_unicode_string(device.driver)
    else:
        assert device.driver is None


@pytest.mark.properties
def test_device_type(device, properties):
    if 'DEVTYPE' in properties:
        assert device.device_type == properties['DEVTYPE']
        assert pytest.is_unicode_string(device.device_type)
    else:
        assert device.device_type is None


def test_device_children(device):
    for child in device.children:
        assert child.parent == device


def test_device_traverse(device):
    child = device
    for parent in device.traverse():
        assert parent == child.parent
        assert child in parent.children
        child = parent


def test_device_find_parent(device):
    parent = device.find_parent(device.subsystem)
    if not parent:
        pytest.xfail('no parent within the same subsystem')
    assert parent.subsystem == device.subsystem
    assert parent in device.traverse()
    assert device in parent.children


def test_device_find_parent_no_devtype_mock(device):
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


def test_device_find_parent_with_devtype_mock(device):
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


@pytest.mark.operator
def test_device_eq(device):
    assert device == device.device_path
    assert device == device
    assert device.parent == device.parent
    assert not (device == device.parent)


@pytest.mark.operator
def test_device_ne(device):
    assert not (device != device.device_path)
    assert not (device != device)
    assert not (device.parent != device.parent)
    assert device != device.parent


@pytest.mark.operator
def test_device_ordering(platform_device, operator):
    with pytest.raises(TypeError) as exc_info:
        operator(platform_device, platform_device)
    assert str(exc_info.value) == 'Device not orderable'


@pytest.mark.operator
def test_device_hash(device):
    assert hash(device) == hash(device.device_path)
    assert hash(device.parent) == hash(device.parent)
    assert hash(device.parent) != hash(device)
