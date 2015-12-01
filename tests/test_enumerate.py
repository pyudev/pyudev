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

import pytest
import mock

from hypothesis import given
from hypothesis import strategies
from hypothesis import Settings

from pyudev import Enumerator

from ._device_tests import _CONTEXT_STRATEGY
from ._device_tests import _DEVICES
from ._device_tests import _UDEV_TEST

@pytest.fixture
def enumerator(request):
    context = request.getfuncargvalue('context')
    return context.list_devices()


class TestEnumerator(object):

    def test_match_subsystem(self, context):
        devices = context.list_devices().match_subsystem('input')
        for device in devices:
            assert device.subsystem == 'input'

    def test_match_subsystem_nomatch(self, context):
        devices = context.list_devices().match_subsystem('input', nomatch=True)
        for device in devices:
            assert device.subsystem != 'input'

    def test_match_subsystem_nomatch_unfulfillable(self, context):
        devices = context.list_devices()
        devices.match_subsystem('input')
        devices.match_subsystem('input', nomatch=True)
        assert not list(devices)

    def test_match_sys_name(self, context):
        devices = context.list_devices().match_sys_name('sda')
        for device in devices:
            assert device.sys_name == 'sda'

    def test_match_property_string(self, context):
        devices = list(context.list_devices().match_property('DRIVER', 'usb'))
        for device in devices:
            assert device['DRIVER'] == 'usb'
            assert device.driver == 'usb'

    def test_match_property_int(self, context):
        devices = list(context.list_devices().match_property(
            'ID_INPUT_KEY', 1))
        for device in devices:
            assert device['ID_INPUT_KEY'] == '1'
            assert device.asint('ID_INPUT_KEY') == 1

    def test_match_property_bool(self, context):
        devices = list(context.list_devices().match_property(
            'ID_INPUT_KEY', True))
        for device in devices:
            assert device['ID_INPUT_KEY'] == '1'
            assert device.asbool('ID_INPUT_KEY')

    def test_match_attribute_nomatch(self, context):
        key = 'driver'
        value = 'usb'
        devices = context.list_devices().match_attribute(
           key,
           value,
           nomatch=True
        )
        for device in devices:
            attributes = device.attributes
            assert attributes.get(key) != value

    def test_match_attribute_nomatch_unfulfillable(self, context):
        devices = context.list_devices()
        devices.match_attribute('driver', 'usb')
        devices.match_attribute('driver', 'usb', nomatch=True)
        assert not list(devices)

    def test_match_attribute_string(self, context):
        devices = list(context.list_devices().match_attribute('driver', 'usb'))
        for device in devices:
            assert device.attributes.get('driver') == b'usb'

    def test_match_attribute_int(self, context):
        # busnum gives us the number of a USB bus.  And any decent system
        # likely has two or more usb buses, so this should work on more or less
        # any system.  I didn't find any other attribute that is likely to be
        # present on a wide range of system, so this is probably as general as
        # possible.  Still it may fail because the attribute isn't present on
        # any device at all on the system running the test
        devices = list(context.list_devices().match_attribute('busnum', 2))
        for device in devices:
            assert device.attributes.get('busnum') == b'2'
            assert device.attributes.asint('busnum') == 2

    def test_match_attribute_bool(self, context):
        # ro tells us whether a volumne is mounted read-only or not.  And any
        # developers system should have at least one readable volume, thus this
        # test should work on all systems these tests are ever run on
        devices = list(context.list_devices().match_attribute('ro', False))
        for device in devices:
            assert device.attributes.get('ro') == b'0'
            assert not device.attributes.asbool('ro')

    @_UDEV_TEST(154, "test_match_tag_mock")
    def test_match_tag_mock(self, context):
        enumerator = context.list_devices()
        funcname = 'udev_enumerate_add_match_tag'
        spec = lambda e, t: None
        with mock.patch.object(enumerator._libudev, funcname,
                               autospec=spec) as func:
            retval = enumerator.match_tag('spam')
            assert retval is enumerator
            func.assert_called_with(enumerator, b'spam')

    @_UDEV_TEST(154, "test_match_tag")
    def test_match_tag(self, context):
        devices = list(context.list_devices().match_tag('seat'))
        for device in devices:
            assert 'seat' in device.tags

    _devices = [d for d in _DEVICES if d.parent]
    if len(_devices) > 0:
        @given(
           _CONTEXT_STRATEGY,
           strategies.sampled_from(_DEVICES).filter(lambda x: x.parent),
           settings=Settings(max_examples=5)
        )
        def test_match_parent(self, context, device):
            parent = device.parent
            children = list(context.list_devices().match_parent(parent))
            assert device in children
            try:
                assert parent in children
            except AssertionError:
                pytest.xfail("rhbz#1255191")
    else:
        def test_match_parent(self):
            pytest.skip("not enough devices with parents")

    @_UDEV_TEST(165, "test_match_is_initialized_mock")
    def test_match_is_initialized_mock(self, context):
        enumerator = context.list_devices()
        funcname = 'udev_enumerate_add_match_is_initialized'
        spec = lambda e: None
        with mock.patch.object(enumerator._libudev, funcname,
                               autospec=spec) as func:
            retval = enumerator.match_is_initialized()
            assert retval is enumerator
            func.assert_called_with(enumerator)

    def test_combined_matches_of_same_type(self, context):
        """
        Test for behaviour as observed in #1
        """
        properties = ('DEVTYPE', 'ID_TYPE')
        devices = context.list_devices()
        for property in properties:
            devices.match_property(property, 'disk')
        for device in devices:
            assert (device.get('DEVTYPE') == 'disk' or
                    device.get('ID_TYPE') == 'disk')

    def test_combined_matches_of_different_types(self, context):
        properties = ('DEVTYPE', 'ID_TYPE')
        devices = context.list_devices().match_subsystem('input')
        for property in properties:
            devices.match_property(property, 'disk')
        devices = list(devices)
        assert not devices

    def test_match(self, context):
        devices = list(context.list_devices().match(
            subsystem='input', ID_INPUT_MOUSE=True, sys_name='mouse0'))
        for device in devices:
            assert device.subsystem == 'input'
            assert device.asbool('ID_INPUT_MOUSE')
            assert device.sys_name == 'mouse0'

    def test_match_passthrough_subsystem(self, enumerator):
        with mock.patch.object(enumerator, 'match_subsystem',
                               autospec=True) as match_subsystem:
            enumerator.match(subsystem=mock.sentinel.subsystem)
            match_subsystem.assert_called_with(mock.sentinel.subsystem)

    def test_match_passthrough_sys_name(self, enumerator):
        with mock.patch.object(enumerator, 'match_sys_name',
                               autospec=True) as match_sys_name:
            enumerator.match(sys_name=mock.sentinel.sys_name)
            match_sys_name.assert_called_with(mock.sentinel.sys_name)

    def test_match_passthrough_tag(self, enumerator):
        with mock.patch.object(enumerator, 'match_tag',
                               autospec=True) as match_tag:
            enumerator.match(tag=mock.sentinel.tag)
            match_tag.assert_called_with(mock.sentinel.tag)

    @_UDEV_TEST(172, "test_match_passthrough_parent")
    def test_match_passthrough_parent(self, enumerator):
        with mock.patch.object(enumerator, 'match_parent',
                               autospec=True) as match_parent:
            enumerator.match(parent=mock.sentinel.parent)
            match_parent.assert_called_with(mock.sentinel.parent)

    def test_match_passthrough_property(self, enumerator):
        with mock.patch.object(enumerator, 'match_property',
                               autospec=True) as match_property:
            enumerator.match(eggs=mock.sentinel.eggs, spam=mock.sentinel.spam)
            assert match_property.call_count == 2
            posargs = [args for args, _ in match_property.call_args_list]
            assert ('spam', mock.sentinel.spam) in posargs
            assert ('eggs', mock.sentinel.eggs) in posargs


class TestContext(object):

    @pytest.mark.match
    def test_list_devices(self, context):
        devices = list(context.list_devices(
            subsystem='input', ID_INPUT_MOUSE=True, sys_name='mouse0'))
        for device in devices:
            assert device.subsystem == 'input'
            assert device.asbool('ID_INPUT_MOUSE')
            assert device.sys_name == 'mouse0'

    @pytest.mark.match
    def test_list_devices_passthrough(self, context):
        with mock.patch.object(Enumerator, 'match') as match:
            context.list_devices(subsystem=mock.sentinel.subsystem,
                                 sys_name=mock.sentinel.sys_name,
                                 tag=mock.sentinel.tag,
                                 parent=mock.sentinel.parent,
                                 prop1=mock.sentinel.prop1,
                                 prop2=mock.sentinel.prop2)
            match.assert_called_with(
                subsystem=mock.sentinel.subsystem,
                sys_name=mock.sentinel.sys_name,
                tag=mock.sentinel.tag,
                parent=mock.sentinel.parent,
                prop1=mock.sentinel.prop1,
                prop2=mock.sentinel.prop2)
