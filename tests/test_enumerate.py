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

from contextlib import nested
from functools import partial

import pytest
import mock

from pyudev import Enumerator


def test_match_subsystem(context):
    devices = context.list_devices().match_subsystem('input')
    assert all(d.subsystem == 'input' for d in devices)


def test_match_sys_name(context):
    devices = context.list_devices().match_sys_name('sda')
    assert all(d.sys_name == 'sda' for d in devices)


def test_match_property_string(context):
    devices = list(context.list_devices().match_property('DRIVER', 'usb'))
    assert all(d['DRIVER'] == 'usb' for d in devices)
    assert all(d.driver == 'usb' for d in devices)


def test_match_property_int(context):
    devices = list(context.list_devices().match_property('ID_INPUT_KEY', 1))
    assert all(d['ID_INPUT_KEY'] == '1' for d in devices)
    assert all(d.asint('ID_INPUT_KEY') == 1 for d in devices)


def test_match_property_bool(context):
    devices = list(context.list_devices().match_property('ID_INPUT_KEY', True))
    assert all(d['ID_INPUT_KEY'] == '1' for d in devices)
    assert all(d.asbool('ID_INPUT_KEY') for d in devices)


@pytest.check_udev_version('>= 154')
def test_match_tags_mock(context):
    add_match_tag = 'udev_enumerate_add_match_tag'
    enumerator = context.list_devices()
    with pytest.patch_libudev(add_match_tag) as add_match_tag:
        retval = enumerator.match_tag('spam')
        assert retval is enumerator
        add_match_tag.assert_called_with(enumerator._enumerator, b'spam')
        args, _ = add_match_tag.call_args
        assert isinstance(args[1], bytes)


@pytest.mark.xfail
@pytest.check_udev_version('>= 154')
def test_match_tags():
    raise NotImplementedError()


@pytest.check_udev_version('>= 165')
def test_match_is_initialized(context):
    match_is_initialized = 'udev_enumerate_add_match_is_initialized'
    with pytest.patch_libudev(match_is_initialized) as match_is_initialized:
        context.list_devices().match_is_initialized()
        assert match_is_initialized.called


def test_combined_matches_of_same_type(context):
    """
    Test for behaviour as observed in #1
    """
    properties = ('DEVTYPE', 'ID_TYPE')
    devices = context.list_devices()
    for property in properties:
        devices.match_property(property, 'disk')
    assert all(any(d.get(p) == 'disk' for p in properties) for d in devices)


def test_combined_matches_of_different_types(context):
    properties = ('DEVTYPE', 'ID_TYPE')
    devices = context.list_devices().match_subsystem('input')
    for property in properties:
        devices.match_property(property, 'disk')
    devices = list(devices)
    assert not devices


def test_match(context):
    devices = list(context.list_devices().match(
        subsystem='input', ID_INPUT_MOUSE=True, sys_name='mouse0'))
    assert all(d.subsystem == 'input' for d in devices)
    assert all(d.asbool('ID_INPUT_MOUSE') for d in devices)
    assert all(d.sys_name == 'mouse0' for d in devices)


def test_match_passthrough(context):
    """
    Test pass-through of all keyword arguments
    """
    enumerator = context.list_devices()
    patch_enum = partial(mock.patch.object, enumerator, mocksignature=True)
    with nested(patch_enum('match_subsystem'),
                patch_enum('match_sys_name'),
                patch_enum('match_tag'),
                patch_enum('match_property')) as (match_subsystem,
                                                  match_sys_name,
                                                  match_tag,
                                                  match_property):
        enumerator.match(subsystem=mock.sentinel.subsystem,
                         sys_name=mock.sentinel.sys_name,
                         tag=mock.sentinel.tag,
                         prop1=mock.sentinel.prop1,
                         prop2=mock.sentinel.prop2)
        match_subsystem.assert_called_with(mock.sentinel.subsystem)
        match_sys_name.assert_called_with(mock.sentinel.sys_name)
        match_tag.assert_called_with(mock.sentinel.tag)
        assert match_property.call_count == 2
        positional_args = [args for args, _ in match_property.call_args_list]
        assert ('prop1', mock.sentinel.prop1) in positional_args
        assert ('prop2', mock.sentinel.prop2) in positional_args


@pytest.mark.match
def test_list_devices(context):
    devices = list(context.list_devices(subsystem='input', ID_INPUT_MOUSE=True,
                                        sys_name='mouse0'))
    assert all(d.subsystem == 'input' for d in devices)
    assert all(d.asbool('ID_INPUT_MOUSE') for d in devices)
    assert all(d.sys_name == 'mouse0' for d in devices)


@pytest.mark.match
def test_list_devices_passthrough(context):
    with mock.patch_object(Enumerator, 'match') as match:
        context.list_devices(subsystem=mock.sentinel.subsystem,
                             sys_name=mock.sentinel.sys_name,
                             tag=mock.sentinel.tag,
                             prop1=mock.sentinel.prop1,
                             prop2=mock.sentinel.prop2)
        match.assert_called_with(
            subsystem=mock.sentinel.subsystem,
            sys_name=mock.sentinel.sys_name,
            tag=mock.sentinel.tag,
            prop1=mock.sentinel.prop1,
            prop2=mock.sentinel.prop2)
