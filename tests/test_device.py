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


import subprocess
import operator

import py.test

from udev import Context, Device

# these are volatile, frequently changing properties, which lead to bogus
# failures during test_device_property, and therefore they are masked and
# shall be ignored for test runs.
PROPERTIES_BLACKLIST = frozenset(
    ['POWER_SUPPLY_CURRENT_NOW', 'POWER_SUPPLY_VOLTAGE_NOW',
     'POWER_SUPPLY_CHARGE_NOW'])


def _read_udev_database():
    udevadm = subprocess.Popen(['udevadm', 'info', '--export-db'],
                               stdout=subprocess.PIPE)
    database = udevadm.communicate()[0].splitlines()
    devices = {}
    current_properties = None
    for line in database:
        line = line.strip()
        if not line:
            continue
        type, value = line.split(': ', 1)
        if type == 'P':
            current_properties = devices.setdefault(value, {})
        elif type == 'E':
            property, value = value.split('=', 1)
            if property in PROPERTIES_BLACKLIST:
                continue
            current_properties[property] = value
    return devices


def pytest_generate_tests(metafunc):
    database = _read_udev_database()
    context = Context()
    if metafunc.function is test_device_property:
        devices = context.list_devices()
        for device in devices:
            properties = database[device.device_path]
            for property, value in properties.iteritems():
                metafunc.addcall(
                    funcargs=dict(device=device, property=property,
                                  expected=value),
                    id='{0.device_path},{1}'.format(device, property))
    elif 'device' in metafunc.funcargnames:
        for device in context.list_devices():
            metafunc.addcall(funcargs=dict(device=device),
                             id='{0.device_path}'.format(device))
    elif 'sys_path' in metafunc.funcargnames:
        for devpath in database:
            sys_path = context.sys_path + devpath
            metafunc.addcall(funcargs=dict(sys_path=sys_path),
                              id=devpath)


def test_device_from_sys_path(sys_path, context):
    device = Device.from_sys_path(context, sys_path)
    assert device is not None
    assert device.sys_path == sys_path
    assert device.device_path == sys_path[len(context.sys_path):]


@py.test.mark.properties
def test_device_property(device, property, expected):
    if property == 'DEVNAME':
        def _strip_devpath(v):
            if v.startswith(device.context.device_path):
                return v[len(device.context.device_path):].lstrip('/')
            return v
        assert _strip_devpath(device[property]) == _strip_devpath(expected)
    else:
        assert device[property] == expected

def test_device_children(device):
    for child in device.children:
        assert child.parent == device


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


def _assert_ordering(device, operator):
    exc_info = py.test.raises(TypeError, lambda: operator(device, device))
    assert str(exc_info.value) == 'Device not orderable'

for operator in (operator.gt, operator.lt, operator.le, operator.ge):
    @py.test.mark.operator
    def foo(device):
        _assert_ordering(device, operator)
    foo.__name__ = 'test_device_{0}'.format(operator.__name__)
    globals()[foo.__name__] = foo


def test_device_hash(device):
    assert hash(device) == hash(device.device_path)
    assert hash(device.parent) == hash(device.parent)
    assert hash(device.parent) != hash(device)
