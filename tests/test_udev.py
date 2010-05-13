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

import py.test

import udev
context = udev.Context()


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
            current_properties[property] = value
    return devices


def pytest_generate_tests(metafunc):
    database = _read_udev_database()
    if metafunc.function == test_device_property:
        devices = context.list_devices()
        for device in devices:
            properties = database[device.device_path]
            for property, value in properties.iteritems():
                metafunc.addcall(
                    funcargs=dict(device=device, property=property,
                                  expected=value),
                    id='{0.device_path},{1}'.format(device, property))


def test_context_syspath():
    assert isinstance(context.sys_path, unicode)
    assert context.sys_path == u'/sys'


def test_context_devpath():
    assert isinstance(context.device_path, unicode)
    assert context.device_path == u'/dev'


@py.test.mark.property
def test_device_property(device, property, expected):
    if property == 'DEVNAME':
        def _strip_devpath(v):
            if v.startswith(device.context.device_path):
                return v[len(device.context.device_path):].lstrip('/')
            return v
        assert _strip_devpath(device[property]) == _strip_devpath(expected)
    else:
        assert device[property] == expected
