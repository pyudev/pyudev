# -*- coding: utf-8 -*-
# Copyright (C) 2010 Sebastian Wiesner <lunaryorn@googlemail.com>

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


import os
import operator
import sys
from itertools import count

import py.test

from pyudev import (Device,
                    DeviceNotFoundAtPathError, DeviceNotFoundByNameError)


def pytest_generate_tests(metafunc):
    args = metafunc.funcargnames
    if 'device_path' in args or 'device' in args:
        devices = py.test.get_device_sample(metafunc.config)
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
    with py.test.raises(DeviceNotFoundAtPathError) as exc_info:
        Device.from_sys_path(context, sys_path)
    error = exc_info.value
    assert error.sys_path == sys_path
    assert str(error) == 'No device at {0!r}'.format(sys_path)


def test_device_from_name(context, device):
    new_device = Device.from_name(context, device.subsystem,
                                  device.sys_name)
    assert new_device == device


def test_device_from_name_no_device_in_existing_subsystem(context):
    with py.test.raises(DeviceNotFoundByNameError) as exc_info:
        Device.from_name(context, 'block', 'foobar')
    error = exc_info.value
    assert error.subsystem == 'block'
    assert error.sys_name == 'foobar'
    assert str(error) == 'No device {0!r} in {1!r}'.format(
        error.sys_name, error.subsystem)


def test_device_from_name_nonexisting_subsystem(context):
    with py.test.raises(DeviceNotFoundByNameError) as exc_info:
        Device.from_name(context, 'no_such_subsystem', 'foobar')
    error = exc_info.value
    assert error.subsystem == 'no_such_subsystem'
    assert error.sys_name == 'foobar'
    assert str(error) == 'No device {0!r} in {1!r}'.format(
        error.sys_name, error.subsystem)


@py.test.mark.properties
def test_device_properties(device, properties):
    properties.pop('DEVNAME', None)
    for n, property in enumerate(properties, start=1):
        assert device[property] == properties[property]
    assert n > 0


@py.test.mark.properties
def test_device_asint(device, properties):
    for n, property in enumerate(properties, start=1):
        value = properties[property]
        try:
            value = int(value)
        except ValueError:
            with py.test.raises(ValueError):
                device.asint(property)
        else:
            assert device.asint(property) == value
    assert n > 0


@py.test.mark.properties
def test_device_asbool(device, properties):
    for n, property in enumerate(properties, start=1):
        value = properties[property]
        if value == '1':
            assert device.asbool(property)
        elif value == '0':
            assert not device.asbool(property)
        else:
            with py.test.raises(ValueError) as exc_info:
                device.asbool(property)
            message = 'Not a boolean value: {0!r}'
            assert str(exc_info.value) == message.format(value)
    assert n > 0


def test_attributes_iter(device, attributes):
    device_attributes = set(device.attributes)
    for attribute in attributes:
        assert attribute in device_attributes
    assert all(py.test.is_unicode_string(a) for a in device_attributes)


def test_attributes_len(device):
    counter = count()
    for _ in device.attributes:
        next(counter)
    assert len(device.attributes) == next(counter)


def test_attributes_contains(device, attributes):
    assert all(a in device.attributes for a in attributes)


def test_attributes_getitem(device, attributes):
    for attribute, value in attributes.items():
        # device attributes *must* be bytes.
        assert isinstance(device.attributes[attribute], bytes)
        value = value.encode(sys.getfilesystemencoding())
        assert device.attributes[attribute] == value


def test_attributes_asstring(device, attributes):
    for attribute, value in attributes.items():
        assert py.test.is_unicode_string(
            device.attributes.asstring(attribute))
        assert device.attributes.asstring(attribute) == value


def test_attributes_asint(device, attributes):
    for attribute, value in attributes.items():
        try:
            value = int(value)
        except ValueError:
            with py.test.raises(ValueError):
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
            with py.test.raises(ValueError) as exc_info:
                device.attributes.asbool(attribute)
            message = 'Not a boolean value: {0!r}'
            assert str(exc_info.value) == message.format(value)


@py.test.mark.properties
def test_device_devname(context, device, all_properties):
    if 'DEVNAME' not in device:
        py.test.xfail('%r has no DEVNAME' % device)
    assert device['DEVNAME'].startswith(context.device_path)
    assert device['DEVNAME'] == os.path.join(context.device_path,
                                             all_properties['DEVNAME'])


@py.test.mark.properties
def test_device_subsystem(device, properties):
    assert device.subsystem == properties['SUBSYSTEM']
    assert py.test.is_unicode_string(device.subsystem)


@py.test.mark.properties
def test_device_sys_name(device):
    assert device.sys_name == os.path.basename(device.device_path)
    assert py.test.is_unicode_string(device.sys_name)


@py.test.mark.properties
def test_device_node(context, device, device_node):
    if device_node:
        assert device.device_node == os.path.join(context.device_path,
                                                  device_node)
        assert py.test.is_unicode_string(device.device_node)
    else:
        assert device.device_node is None


@py.test.mark.properties
def test_device_links(context, device, device_links):
    assert sorted(device.device_links) == sorted(
        os.path.join(context.device_path, l) for l in device_links)
    assert all(py.test.is_unicode_string(l) for l in device.device_links)


def test_device_tags():
    raise NotImplementedError()


@py.test.mark.properties
def test_device_driver(device, properties):
    if 'DRIVER' in properties:
        assert device.driver == properties['DRIVER']
        assert py.test.is_unicode_string(device.driver)
    else:
        assert device.driver is None


def test_device_children(device):
    for child in device.children:
        assert child.parent == device


def test_device_traverse(device):
    child = device
    for parent in device.traverse():
        assert parent == child.parent
        assert child in parent.children
        child = parent


@py.test.mark.operator
def test_device_eq(device):
    assert device == device.device_path
    assert device == device
    assert device.parent == device.parent
    assert not (device == device.parent)


@py.test.mark.operator
def test_device_ne(device):
    assert not (device != device.device_path)
    assert not (device != device)
    assert not (device.parent != device.parent)
    assert device != device.parent


@py.test.mark.operator
def test_device_ordering(platform_device, operator):
    with py.test.raises(TypeError) as exc_info:
        operator(platform_device, platform_device)
    assert str(exc_info.value) == 'Device not orderable'


@py.test.mark.operator
def test_device_hash(device):
    assert hash(device) == hash(device.device_path)
    assert hash(device.parent) == hash(device.parent)
    assert hash(device.parent) != hash(device)
