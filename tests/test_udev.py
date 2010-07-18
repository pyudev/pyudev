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
import sys
import subprocess
import operator

import py.test

import udev
context = udev.Context()


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


@py.test.mark.context
def test_context_syspath():
    assert isinstance(context.sys_path, unicode)
    assert context.sys_path == u'/sys'


@py.test.mark.context
def test_context_devpath():
    assert isinstance(context.device_path, unicode)
    assert context.device_path == u'/dev'


@py.test.mark.conversion
def test__assert_bytes():
    assert isinstance(udev._assert_bytes(u'hello world'), str)
    hello = b'hello world'
    assert udev._assert_bytes(hello) is hello


@py.test.mark.conversion
def test__property_value_to_bytes_string():
    hello = u'hello world'.encode(sys.getfilesystemencoding())
    assert udev._property_value_to_bytes(hello) is hello
    assert isinstance(udev._property_value_to_bytes(u'hello world'), str)
    assert udev._property_value_to_bytes(u'hello world') == hello


@py.test.mark.conversion
def test__property_value_to_bytes_int():
    assert udev._property_value_to_bytes(10000) == '10000'


@py.test.mark.conversion
def test__property_value_to_bytes_bool():
    assert udev._property_value_to_bytes(True) == '1'
    assert udev._property_value_to_bytes(False) == '0'


@py.test.mark.util
def test__check_call_zero_result():
    assert udev._check_call(lambda x: 0, 'hello') == 0


@py.test.mark.util
def test__check_call_nonzero_result():
    py.test.raises(EnvironmentError, udev._check_call, lambda: -1)
    py.test.raises(EnvironmentError, udev._check_call, lambda: 1)
    py.test.raises(EnvironmentError, udev._check_call, lambda: 100)


@py.test.mark.util
def test__check_call_invalid_args():
    py.test.raises(TypeError, udev._check_call, lambda x: 0)
    py.test.raises(TypeError, udev._check_call, lambda x: 0, 1, 2, 3)


@py.test.mark.filter
def test_match_subsystem():
    devices = context.list_devices().match_subsystem('input')
    for n, device in enumerate(devices, start=1):
        assert device.subsystem == 'input'
    assert n > 0


@py.test.mark.filter
def test_match_property_string():
    devices = context.list_devices().match_property('DRIVER', 'usb')
    for n, device in enumerate(devices, start=1):
        assert device['DRIVER'] == 'usb'
    assert n > 0


@py.test.mark.filter
def test_match_property_int():
    devices = context.list_devices().match_property('ID_INPUT_KEY', 1)
    for n, device in enumerate(devices, start=1):
        assert device['ID_INPUT_KEY'] == '1'
    assert n > 0


@py.test.mark.filter
def test_match_property_bool():
    devices = context.list_devices().match_property('ID_INPUT_KEY', True)
    for n, device in enumerate(devices, start=1):
        assert device['ID_INPUT_KEY'] == '1'
    assert n > 0


@py.test.mark.filter
def test_match_toplevel():
    devices = context.list_devices().match_toplevel()
    for n, device in enumerate(devices, start=1):
        assert device.parent is None
    assert n > 0


@py.test.mark.device
def test_device_from_sys_path(sys_path):
    device = udev.Device.from_sys_path(context, sys_path)
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


@py.test.mark.device
@py.test.mark.operator
def test_device_eq(device):
    assert device == device.device_path
    assert device == device
    assert device.parent == device.parent
    assert not (device == device.parent)


@py.test.mark.device
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
    @py.test.mark.device
    @py.test.mark.operator
    def foo(device):
        _assert_ordering(device, operator)
    foo.__name__ = 'test_device_{0}'.format(operator.__name__)
    globals()[foo.__name__] = foo


@py.test.mark.device
def test_device_hash(device):
    assert hash(device) == hash(device.device_path)
    assert hash(device.parent) == hash(device.parent)
    assert hash(device.parent) != hash(device)

