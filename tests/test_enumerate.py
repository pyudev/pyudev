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

from hypothesis import assume
from hypothesis import given
from hypothesis import note
from hypothesis import settings
from hypothesis import strategies

from pyudev import Enumerator

from ._constants import _ATTRIBUTE_STRATEGY
from ._constants import _CONTEXT_STRATEGY
from ._constants import _DEVICES
from ._constants import _PROPERTY_STRATEGY
from ._constants import _SUBSYSTEM_STRATEGY
from ._constants import _SYSNAME_STRATEGY
from ._constants import _TAG_STRATEGY
from ._constants import _UDEV_TEST
from ._constants import _UDEV_VERSION

from .utils import failed_health_check_wrapper

def _is_int(value):
    try:
        int(value)
        return True
    except (TypeError, ValueError):
        return False

def _is_bool(value):
    try:
        return int(value) in (0, 1)
    except (TypeError, ValueError):
        return False


class TestEnumerator(object):
    """
    Test the Enumerator class.
    """

    @failed_health_check_wrapper
    @given(_CONTEXT_STRATEGY, _SUBSYSTEM_STRATEGY)
    @settings(max_examples=5)
    def test_match_subsystem(self, context, subsystem):
        """
        Subsystem match matches devices w/ correct subsystem.
        """
        devices = context.list_devices().match_subsystem(subsystem)
        assert all(device.subsystem == subsystem for device in devices)

    @failed_health_check_wrapper
    @given(_CONTEXT_STRATEGY, _SUBSYSTEM_STRATEGY)
    @settings(max_examples=5)
    def test_match_subsystem_nomatch(self, context, subsystem):
        """
        Subsystem no match gets no subsystem with subsystem.
        """
        devices = \
           context.list_devices().match_subsystem(subsystem, nomatch=True)
        assert all(d.subsystem is not None and d.subsystem != subsystem \
           for d in devices)

    @failed_health_check_wrapper
    @given(_CONTEXT_STRATEGY, _SUBSYSTEM_STRATEGY)
    @settings(max_examples=5)
    def test_match_subsystem_nomatch_unfulfillable(self, context, subsystem):
        """
        Combining match and no match should give an empty result.
        """
        devices = context.list_devices()
        devices.match_subsystem(subsystem)
        devices.match_subsystem(subsystem, nomatch=True)
        assert not list(devices)

    @failed_health_check_wrapper
    @given(_CONTEXT_STRATEGY, _SUBSYSTEM_STRATEGY)
    @settings(max_examples=5)
    def test_match_subsystem_nomatch_complete(self, context, subsystem):
        """
        Test that w/ respect to the universe of devices returned by
        list_devices() a match and its inverse are complements of each other.

        Note that list_devices() omits devices that have no subsystem,
        so with respect to the whole universe of devices, the two are
        not complements of each other.
        """
        m_devices = set(context.list_devices().match_subsystem(subsystem))
        nm_devices = \
           set(context.list_devices().match_subsystem(subsystem, nomatch=True))

        assert not m_devices.intersection(nm_devices)

        devices = set(context.list_devices())
        assert devices == m_devices.union(nm_devices)

    @failed_health_check_wrapper
    @given(_CONTEXT_STRATEGY, _SYSNAME_STRATEGY)
    @settings(max_examples=5)
    def test_match_sys_name(self, context, sysname):
        """
        A sysname lookup only gives devices with that sysname.
        """
        devices = context.list_devices().match_sys_name(sysname)
        assert all(device.sys_name == sysname for device in devices)

    @failed_health_check_wrapper
    @given(_CONTEXT_STRATEGY, _PROPERTY_STRATEGY)
    @settings(max_examples=50)
    def test_match_property_string(self, context, pair):
        """
        Match property only gets devices with that property.
        """
        key, value = pair
        devices = context.list_devices().match_property(key, value)
        assert all(device.properties[key] == value for device in devices)

    @failed_health_check_wrapper
    @given(
       _CONTEXT_STRATEGY,
       _PROPERTY_STRATEGY.filter(lambda x: _is_int(x[1]))
    )
    @settings(max_examples=50)
    def test_match_property_int(self, context, pair):
        """
        For a property that might plausibly have an integer value, search
        using the integer value and verify that the result all match.
        """
        key, value = pair
        devices = context.list_devices().match_property(key, int(value))
        assert all(device[key] == value and device.asint(key) == int(value) \
           for device in devices)

    @failed_health_check_wrapper
    @given(
       _CONTEXT_STRATEGY,
       _PROPERTY_STRATEGY.filter(lambda x: _is_bool(x[1]))
    )
    @settings(max_examples=10)
    def test_match_property_bool(self, context, pair):
        """
        Verify that a probably boolean property lookup works.
        """
        key, value = pair
        bool_value = True if int(value) == 1 else False
        devices = context.list_devices().match_property(key, bool_value)
        assert all(
           device.properties[key] == value and \
           device.asbool(key) == bool_value \
           for device in devices
        )

    @failed_health_check_wrapper
    @given(
       _CONTEXT_STRATEGY,
       _ATTRIBUTE_STRATEGY.filter(lambda p: p[1] is not None)
    )
    def test_match_attribute_nomatch(self, context, pair):
        """
        Test that nomatch returns no devices with attribute value match.
        """
        key, value = pair
        if _UDEV_VERSION <= 222:
            assume(not value.startswith(b"\\"))

        devices = list(
           context.list_devices().match_attribute(key, value, nomatch=True)
        )

        all(device.attributes.get(key) != value for device in devices)

        note(
           " ".join(
              ("Device: %s, actual: %s" % (d, d.attributes.get(key))) \
                 for d in devices if d.attributes.get(key) == value
           )
        )

    @failed_health_check_wrapper
    @given(
       _CONTEXT_STRATEGY,
       _ATTRIBUTE_STRATEGY.filter(lambda p: p[1] is not None)
    )
    @settings(max_examples=10)
    def test_match_attribute_backslash(self, context, pair):
        """
        Test that no matches with value starting with a backslash work.
        """
        key, value = pair
        assume(value.startswith(b"\\"))
        devices = context.list_devices().match_attribute(
           key,
           value
        )
        assert list(devices) == []

        devices = context.list_devices().match_attribute(
           key,
           value,
           nomatch=True
        )
        assert any(device.attributes.get(key) == value for device in devices)

    @failed_health_check_wrapper
    @given(
       _CONTEXT_STRATEGY,
       _ATTRIBUTE_STRATEGY.filter(lambda p: p[1] is not None)
    )
    @settings(max_examples=50)
    def test_match_attribute_nomatch_unfulfillable(self, context, pair):
        """
        Match and no match for a key/value gives empty set.
        """
        key, value = pair
        devices = context.list_devices()
        devices.match_attribute(key, value)
        devices.match_attribute(key, value, nomatch=True)
        assert not list(devices)

    @failed_health_check_wrapper
    @given(
       _CONTEXT_STRATEGY,
       _ATTRIBUTE_STRATEGY.filter(lambda p: p[1] is not None)
    )
    @settings(max_examples=50)
    def test_match_attribute_nomatch_complete(self, context, pair):
        """
        Test that w/ respect to the universe of devices returned by
        list_devices() a match and its inverse are complements of each other.
        """
        key, value = pair
        m_devices = frozenset(
           context.list_devices().match_attribute(key, value)
        )
        nm_devices = frozenset(
           context.list_devices().match_attribute(key, value, nomatch=True)
        )

        assert not m_devices.intersection(nm_devices)

        devices = frozenset(context.list_devices())
        assert devices == m_devices.union(nm_devices)

    @failed_health_check_wrapper
    @given(
       _CONTEXT_STRATEGY,
       _ATTRIBUTE_STRATEGY.filter(lambda p: p[1] is not None)
    )
    @settings(max_examples=50)
    def test_match_attribute_string(self, context, pair):
        """
        Test that matching attribute as string works.
        """
        key, value = pair
        devices = context.list_devices().match_attribute(key, value)
        assert all(device.attributes.get(key) == value for device in devices)

    @failed_health_check_wrapper
    @given(
       _CONTEXT_STRATEGY,
       _ATTRIBUTE_STRATEGY.filter(lambda x: _is_int(x[1]))
    )
    @settings(max_examples=50)
    def test_match_attribute_int(self, context, pair):
        """
        Test matching integer attribute.
        """
        key, value = pair
        int_value = int(value)
        devices = context.list_devices().match_attribute(key, int_value)
        for device in devices:
            attributes = device.attributes
            assert attributes.get(key) == value
            assert device.attributes.asint(key) == int_value

    @failed_health_check_wrapper
    @given(
       _CONTEXT_STRATEGY,
       _ATTRIBUTE_STRATEGY.filter(lambda x: _is_bool(x[1]))
    )
    @settings(max_examples=50)
    def test_match_attribute_bool(self, context, pair):
        """
        Test matching boolean attribute.
        """
        key, value = pair
        bool_value = True if int(value) == 1 else False
        devices = context.list_devices().match_attribute(key, bool_value)
        for device in devices:
            attributes = device.attributes
            assert attributes.get(key) == value
            assert attributes.asbool(key) == bool_value

    @_UDEV_TEST(154, "test_match_tag")
    @failed_health_check_wrapper
    @given(_CONTEXT_STRATEGY, _TAG_STRATEGY)
    @settings(max_examples=50)
    def test_match_tag(self, context, tag):
        """
        Test that matches returned for tag actually have tag.
        """
        devices = context.list_devices().match_tag(tag)
        assert all(tag in device.tags for device in devices)

    _devices = [d for d in _DEVICES if d.parent]
    @pytest.mark.skipif(len(_devices) == 0, reason="no device with parent")
    @given(_CONTEXT_STRATEGY, strategies.sampled_from(_devices))
    @settings(max_examples=5, min_satisfying_examples=1)
    def test_match_parent(self, context, device):
        """
        For a given device, verify that it is in its parent's children.

        Verify that the parent is also among the device's children,
        unless the parent lacks a subsystem

        See: rhbz#1255191
        """
        parent = device.parent
        children = list(context.list_devices().match_parent(parent))
        assert device in children
        if _UDEV_VERSION <= 175:
            assert parent in children
        else:
            if parent.subsystem is not None:
                assert parent in children
            else:
                assert parent not in children


class TestEnumeratorMatchCombinations(object):
    """
    Test combinations of matches.
    """

    def test_combined_matches_of_same_type(self, context):
        """
        Test for behaviour as observed in #1
        """
        properties = ('DEVTYPE', 'ID_TYPE')
        devices = context.list_devices()
        for prop in properties:
            devices.match_property(prop, 'disk')
        for device in devices:
            assert (device.get('DEVTYPE') == 'disk' or
                    device.get('ID_TYPE') == 'disk')

    def test_combined_matches_of_different_types(self, context):
        properties = ('DEVTYPE', 'ID_TYPE')
        devices = context.list_devices().match_subsystem('input')
        for prop in properties:
            devices.match_property(prop, 'disk')
        devices = list(devices)
        assert not devices

    def test_match(self, context):
        devices = list(context.list_devices().match(
            subsystem='input', ID_INPUT_MOUSE=True, sys_name='mouse0'))
        for device in devices:
            assert device.subsystem == 'input'
            assert device.asbool('ID_INPUT_MOUSE')
            assert device.sys_name == 'mouse0'


class TestEnumeratorMatchMethod(object):
    """
    Test the behavior of Enumerator.match.

    Only methods that test behavior of this method by patching the Enumerator
    object with the methods that match() should invoke belong here.
    """

    _ENUMERATOR_STRATEGY = _CONTEXT_STRATEGY.map(lambda x: x.list_devices())

    @given(_ENUMERATOR_STRATEGY)
    @settings(max_examples=1)
    def test_match_passthrough_subsystem(self, enumerator):
        """
        Test that special keyword subsystem results in a match_subsystem call.
        """
        with mock.patch.object(enumerator, 'match_subsystem',
                               autospec=True) as match_subsystem:
            enumerator.match(subsystem=mock.sentinel.subsystem)
            match_subsystem.assert_called_with(mock.sentinel.subsystem)

    @given(_ENUMERATOR_STRATEGY)
    @settings(max_examples=1)
    def test_match_passthrough_sys_name(self, enumerator):
        """
        Test that special keyword sys_name results in a match_sys_name call.
        """
        with mock.patch.object(enumerator, 'match_sys_name',
                               autospec=True) as match_sys_name:
            enumerator.match(sys_name=mock.sentinel.sys_name)
            match_sys_name.assert_called_with(mock.sentinel.sys_name)

    @given(_ENUMERATOR_STRATEGY)
    @settings(max_examples=1)
    def test_match_passthrough_tag(self, enumerator):
        """
        Test that special keyword tag results in a match_tag call.
        """
        with mock.patch.object(enumerator, 'match_tag',
                               autospec=True) as match_tag:
            enumerator.match(tag=mock.sentinel.tag)
            match_tag.assert_called_with(mock.sentinel.tag)

    @_UDEV_TEST(172, "test_match_passthrough_parent")
    @given(_ENUMERATOR_STRATEGY)
    @settings(max_examples=1)
    def test_match_passthrough_parent(self, enumerator):
        """
        Test that special keyword 'parent' results in a match parent call.
        """
        with mock.patch.object(enumerator, 'match_parent',
                               autospec=True) as match_parent:
            enumerator.match(parent=mock.sentinel.parent)
            match_parent.assert_called_with(mock.sentinel.parent)

    @given(_ENUMERATOR_STRATEGY)
    @settings(max_examples=1)
    def test_match_passthrough_property(self, enumerator):
        """
        Test that non-special keyword args are treated as properties.
        """
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
