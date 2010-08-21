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

from udev import Device


def pytest_generate_tests(metafunc):
    args = metafunc.funcargnames
    if 'device_path' in args or 'device' in args:
        devices = py.test.get_device_sample(metafunc.config)
        for device_path in devices:
            metafunc.addcall(id=device_path, param=device_path)


def test_device_from_sys_path(context, sys_path, device_path):
    device = Device.from_sys_path(context, sys_path)
    assert device is not None
    assert device.sys_path == sys_path
    assert device.device_path == device_path


@py.test.mark.properties
def test_device_properties(device, properties):
    properties.pop('DEVNAME', None)
    for n, property in enumerate(properties, start=1):
        assert device[property] == properties[property]
    assert n > 0


@py.test.mark.properties
def test_device_devname(context, device, properties):
    if 'DEVNAME' not in device:
        py.test.xfail('%r has no DEVNAME' % device)
    assert device['DEVNAME'].startswith(context.device_path)
    assert device['DEVNAME'] == os.path.join(context.device_path,
                                             properties['DEVNAME'])


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
