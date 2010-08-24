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

import py.test

from pyudev import Device, NoSuchDeviceError


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


def test_device_from_sys_path_no_such_device(context):
    sys_path = 'there_will_not_be_such_a_device'
    with py.test.raises(NoSuchDeviceError) as exc_info:
        Device.from_sys_path(context, sys_path)
    error = exc_info.value
    assert error.sys_path == sys_path
    assert str(error) == 'No such device: {0!r}'.format(sys_path)


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
            message = 'Invalid value for boolean property: {0!r}'
            assert str(exc_info.value) == message.format(value)
    assert n > 0


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
