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


import pytest


def test_match_subsystem(context):
    devices = context.list_devices().match_subsystem('input')
    for n, device in enumerate(devices, start=1):
        assert device.subsystem == 'input'
    assert n > 0


def test_match_property_string(context):
    devices = context.list_devices().match_property('DRIVER', 'usb')
    for n, device in enumerate(devices, start=1):
        assert device['DRIVER'] == 'usb'
    assert n > 0


def test_match_property_int(context):
    devices = context.list_devices().match_property('ID_INPUT_KEY', 1)
    for n, device in enumerate(devices, start=1):
        assert device['ID_INPUT_KEY'] == '1'
    assert n > 0


def test_match_property_bool(context):
    devices = context.list_devices().match_property('ID_INPUT_KEY', True)
    for n, device in enumerate(devices, start=1):
        assert device['ID_INPUT_KEY'] == '1'
    assert n > 0


def test_match_tags(context):
    raise NotImplementedError()


def test_combined_matches_of_same_type(context):
    """
    Test for behaviour as observed in #1
    """
    properties = ('DEVTYPE', 'ID_TYPE')
    devices = context.list_devices()
    for property in properties:
        devices.match_property(property, 'disk')
    for n, device in enumerate(devices, start=1):
        assert any(device.get(p) == 'disk' for p in properties)
    assert n > 0


def test_combined_matches_of_different_types(context):
    properties = ('DEVTYPE', 'ID_TYPE')
    devices = context.list_devices().match_subsystem('input')
    for property in properties:
        devices.match_property(property, 'disk')
    devices = list(devices)
    assert not devices


def test_match(context):
    devices = context.list_devices().match(
        subsystem='input', ID_INPUT_KEY=True)
    for n, device in enumerate(devices, start=1):
        assert device.subsystem == 'input'
        assert device['ID_INPUT_KEY'] == '1'


@pytest.mark.match
def test_list_devices(context):
    devices = context.list_devices(subsystem='input', ID_INPUT_KEY=True)
    for n, device in enumerate(devices, start=1):
        assert device.subsystem == 'input'
        assert device['ID_INPUT_KEY'] == '1'
