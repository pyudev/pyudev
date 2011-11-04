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

from functools import partial

import pytest
import mock

from pyudev import Enumerator


def pytest_generate_tests(metafunc):
    if 'device' in metafunc.funcargnames:
        devices = pytest.get_device_sample(metafunc.config)
        for device_path in devices:
            metafunc.addcall(id=device_path, param=device_path)


def pytest_funcarg__enumerator(request):
    context = request.getfuncargvalue('context')
    return context.list_devices()


class TestEnumerator(object):

    def test_match_subsystem(self, context):
        devices = context.list_devices().match_subsystem('input')
        assert all(d.subsystem == 'input' for d in devices)

    def test_match_subsystem_nomatch(self, context):
        devices = context.list_devices().match_subsystem('input', nomatch=True)
        assert all(d.subsystem != 'input' for d in devices)

    def test_match_subsystem_nomatch_unfulfillable(self, context):
        devices = context.list_devices()
        devices.match_subsystem('input')
        devices.match_subsystem('input', nomatch=True)
        assert not list(devices)

    def test_match_sys_name(self, context):
        devices = context.list_devices().match_sys_name('sda')
        assert all(d.sys_name == 'sda' for d in devices)

    def test_match_property_string(self, context):
        devices = list(context.list_devices().match_property('DRIVER', 'usb'))
        assert all(d['DRIVER'] == 'usb' for d in devices)
        assert all(d.driver == 'usb' for d in devices)

    def test_match_property_int(self, context):
        devices = list(context.list_devices().match_property(
            'ID_INPUT_KEY', 1))
        assert all(d['ID_INPUT_KEY'] == '1' for d in devices)
        assert all(d.asint('ID_INPUT_KEY') == 1 for d in devices)

    def test_match_property_bool(self, context):
        devices = list(context.list_devices().match_property(
            'ID_INPUT_KEY', True))
        assert all(d['ID_INPUT_KEY'] == '1' for d in devices)
        assert all(d.asbool('ID_INPUT_KEY') for d in devices)

    def test_match_attribute_nomatch(self, context):
        devices = context.list_devices().match_attribute(
            'driver', 'usb', nomatch=True)
        assert all(d.attributes.get('driver') != 'usb' for d in devices)

    def test_match_attribute_nomatch_unfulfillable(self, context):
        devices = context.list_devices()
        devices.match_attribute('driver', 'usb')
        devices.match_attribute('driver', 'usb', nomatch=True)
        assert not list(devices)

    def test_match_attribute_string(self, context):
        devices = list(context.list_devices().match_attribute('driver', 'usb'))
        assert all(d.attributes['driver'] == b'usb' for d in devices)

    def test_match_attribute_int(self, context):
        # busnum gives us the number of a USB bus.  And any decent system
        # likely has two or more usb buses, so this should work on more or less
        # any system.  I didn't find any other attribute that is likely to be
        # present on a wide range of system, so this is probably as general as
        # possible.  Still it may fail because the attribute isn't present on
        # any device at all on the system running the test
        devices = list(context.list_devices().match_attribute('busnum', 2))
        assert all(d.attributes['busnum'] == b'2' for d in devices)
        assert all(d.attributes.asint('busnum') == 2 for d in devices)

    def test_match_attribute_bool(self, context):
        # ro tells us whether a volumne is mounted read-only or not.  And any
        # developers system should have at least one readable volume, thus this
        # test should work on all systems these tests are ever run on
        devices = list(context.list_devices().match_attribute('ro', False))
        assert all(d.attributes['ro'] == b'0' for d in devices)
        assert all(not d.attributes.asbool('ro') for d in devices)

    @pytest.need_udev_version('>= 154')
    def test_match_tag_mock(self, context):
        add_match_tag = 'udev_enumerate_add_match_tag'
        enumerator = context.list_devices()
        with pytest.patch_libudev(add_match_tag) as add_match_tag:
            retval = enumerator.match_tag('spam')
            assert retval is enumerator
            add_match_tag.assert_called_with(enumerator, b'spam')
            args, _ = add_match_tag.call_args
            assert isinstance(args[1], bytes)

    @pytest.need_udev_version('>= 154')
    def test_match_tag(self, context):
        devices = list(context.list_devices().match_tag('seat'))
        assert all('seat' in d.tags for d in devices)

    @pytest.need_udev_version('>= 172')
    def test_match_parent(self, context, device):
        parent = device.parent
        if parent is None:
            pytest.skip('Device {0!r} has no parent'.format(device))
        else:
            children = list(context.list_devices().match_parent(parent))
            assert device in children
            assert parent in children

    @pytest.need_udev_version('>= 165')
    def test_match_is_initialized(self, context):
        match_is_initialized = 'udev_enumerate_add_match_is_initialized'
        with pytest.patch_libudev(match_is_initialized) as match_is_initialized:
            context.list_devices().match_is_initialized()
            assert match_is_initialized.called

    def test_combined_matches_of_same_type(self, context):
        """
        Test for behaviour as observed in #1
        """
        properties = ('DEVTYPE', 'ID_TYPE')
        devices = context.list_devices()
        for property in properties:
            devices.match_property(property, 'disk')
        assert all(any(d.get(p) == 'disk' for p in properties) for d in devices)

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
        assert all(d.subsystem == 'input' for d in devices)
        assert all(d.asbool('ID_INPUT_MOUSE') for d in devices)
        assert all(d.sys_name == 'mouse0' for d in devices)

    def test_match_passthrough_subsystem(self, enumerator):
        with mock.patch.object(enumerator, 'match_subsystem',
                               mocksignature=True) as match_subsystem:
            enumerator.match(subsystem=mock.sentinel.subsystem)
            match_subsystem.assert_called_with(mock.sentinel.subsystem, False)

    def test_match_passthrough_sys_name(self, enumerator):
        with mock.patch.object(enumerator, 'match_sys_name',
                               mocksignature=True) as match_sys_name:
            enumerator.match(sys_name=mock.sentinel.sys_name)
            match_sys_name.assert_called_with(mock.sentinel.sys_name)

    def test_match_passthrough_tag(self, enumerator):
        with mock.patch.object(enumerator, 'match_tag',
                               mocksignature=True) as match_tag:
            enumerator.match(tag=mock.sentinel.tag)
            match_tag.assert_called_with(mock.sentinel.tag)

    @pytest.need_udev_version('>= 172')
    def test_match_passthrough_parent(self, enumerator):
        with mock.patch.object(enumerator, 'match_parent',
                               mocksignature=True) as match_parent:
            enumerator.match(parent=mock.sentinel.parent)
            match_parent.assert_called_with(mock.sentinel.parent)

    def test_match_passthrough_property(self, enumerator):
        with mock.patch.object(enumerator, 'match_property',
                               mocksignature=True) as match_property:
            enumerator.match(eggs=mock.sentinel.eggs, spam=mock.sentinel.spam)
            assert match_property.call_count == 2
            posargs = [args for args, _ in match_property.call_args_list]
            assert ('spam', mock.sentinel.spam) in posargs
            assert ('eggs', mock.sentinel.eggs) in posargs


class TestContext(object):

    @pytest.mark.match
    def test_list_devices(self, context):
        devices = list(context.list_devices(subsystem='input', ID_INPUT_MOUSE=True,
                                            sys_name='mouse0'))
        assert all(d.subsystem == 'input' for d in devices)
        assert all(d.asbool('ID_INPUT_MOUSE') for d in devices)
        assert all(d.sys_name == 'mouse0' for d in devices)

    @pytest.mark.match
    def test_list_devices_passthrough(self, context):
        with mock.patch_object(Enumerator, 'match') as match:
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
