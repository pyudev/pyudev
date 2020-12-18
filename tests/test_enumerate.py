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

# isort: FUTURE
from __future__ import absolute_import, division, print_function, unicode_literals

# isort: THIRDPARTY
from hypothesis import given, settings, strategies

from ._constants import (
    _ATTRIBUTE_STRATEGY,
    _CONTEXT_STRATEGY,
    _MATCH_PROPERTY_STRATEGY,
    _SUBSYSTEM_STRATEGY,
    _SYSNAME_STRATEGY,
    _TAG_STRATEGY,
    _UDEV_TEST,
    device_strategy,
)
from .utils import failed_health_check_wrapper

try:
    from unittest import mock
except ImportError:
    import mock


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


def _test_direct_and_complement(context, devices, func):
    """
    Test that results are correct and that complement holds.

    :param Context context: the libudev context
    :param devices: the devices that match
    :type devices: frozenset of Device
    :param func: the property to test
    :type func: device -> bool
    """
    assert [device for device in devices if not func(device)] == []
    complement = frozenset(context.list_devices()) - devices
    assert [device for device in complement if func(device)] == []


def _test_intersection_and_union(context, matches, nomatches):
    """
    Test that intersection is empty and union is all of devices.

    :param matches: the matching devices
    :type matches: frozenset of Device
    :param nomatches: the non-matching devices
    :type nomatches: frozenset of Device
    """
    assert matches & nomatches == frozenset()
    assert matches | nomatches == frozenset(context.list_devices())


class TestEnumerator(object):
    """
    Test the Enumerator class.
    """

    @failed_health_check_wrapper
    @given(_CONTEXT_STRATEGY, _SUBSYSTEM_STRATEGY)
    @settings(max_examples=10)
    def test_match_subsystem(self, context, subsystem):
        """
        Subsystem match matches devices w/ correct subsystem.
        """
        _test_direct_and_complement(
            context,
            frozenset(context.list_devices().match_subsystem(subsystem)),
            lambda d: d.subsystem == subsystem,
        )

    @failed_health_check_wrapper
    @given(_CONTEXT_STRATEGY, _SUBSYSTEM_STRATEGY)
    @settings(max_examples=1)
    def test_match_subsystem_nomatch(self, context, subsystem):
        """
        Subsystem no match gets no subsystem with subsystem.
        """
        _test_direct_and_complement(
            context,
            frozenset(context.list_devices().match_subsystem(subsystem, nomatch=True)),
            lambda d: d.subsystem != subsystem,
        )

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
    @settings(max_examples=1)
    def test_match_subsystem_nomatch_complete(self, context, subsystem):
        """
        Test that w/ respect to the universe of devices returned by
        list_devices() a match and its inverse are complements of each other.

        Note that list_devices() omits devices that have no subsystem,
        so with respect to the whole universe of devices, the two are
        not complements of each other.
        """
        m_devices = frozenset(context.list_devices().match_subsystem(subsystem))
        nm_devices = frozenset(
            context.list_devices().match_subsystem(subsystem, nomatch=True)
        )
        _test_intersection_and_union(context, m_devices, nm_devices)

    @failed_health_check_wrapper
    @given(_CONTEXT_STRATEGY, _SYSNAME_STRATEGY)
    @settings(max_examples=5)
    def test_match_sys_name(self, context, sysname):
        """
        A sysname lookup only gives devices with that sysname.
        """
        _test_direct_and_complement(
            context,
            frozenset(context.list_devices().match_sys_name(sysname)),
            lambda d: d.sys_name == sysname,
        )

    @failed_health_check_wrapper
    @given(_CONTEXT_STRATEGY, _MATCH_PROPERTY_STRATEGY)
    @settings(max_examples=25)
    def test_match_property_string(self, context, pair):
        """
        Match property only gets devices with that property.
        """
        key, value = pair
        _test_direct_and_complement(
            context,
            frozenset(context.list_devices().match_property(key, value)),
            lambda d: d.properties.get(key) == value,
        )

    @failed_health_check_wrapper
    @given(_CONTEXT_STRATEGY, _MATCH_PROPERTY_STRATEGY.filter(lambda x: _is_int(x[1])))
    @settings(max_examples=50)
    def test_match_property_int(self, context, pair):
        """
        For a property that might plausibly have an integer value, search
        using the integer value and verify that the result all match.
        """
        key, value = pair
        devices = context.list_devices().match_property(key, int(value))
        assert all(
            device.properties[key] == value
            and device.properties.asint(key) == int(value)
            for device in devices
        )

    @failed_health_check_wrapper
    @given(_CONTEXT_STRATEGY, _MATCH_PROPERTY_STRATEGY.filter(lambda x: _is_bool(x[1])))
    @settings(max_examples=10)
    def test_match_property_bool(self, context, pair):
        """
        Verify that a probably boolean property lookup works.
        """
        key, value = pair
        bool_value = True if int(value) == 1 else False
        devices = context.list_devices().match_property(key, bool_value)
        assert all(
            device.properties[key] == value
            and device.properties.asbool(key) == bool_value
            for device in devices
        )

    @_UDEV_TEST(154, "test_match_tag")
    @failed_health_check_wrapper
    @given(_CONTEXT_STRATEGY, _TAG_STRATEGY)
    @settings(max_examples=50)
    def test_match_tag(self, context, tag):
        """
        Test that matches returned for tag actually have tag.
        """
        _test_direct_and_complement(
            context,
            frozenset(context.list_devices().match_tag(tag)),
            lambda d: tag in d.tags,
        )

    @failed_health_check_wrapper
    @given(
        _CONTEXT_STRATEGY, device_strategy(filter_func=lambda d: d.parent is not None)
    )
    @settings(max_examples=5)
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


class TestEnumeratorMatchCombinations(object):
    """
    Test combinations of matches.
    """

    @given(
        _CONTEXT_STRATEGY,
        strategies.lists(
            elements=_MATCH_PROPERTY_STRATEGY,
            min_size=2,
            max_size=3,
            unique_by=lambda p: p[0],
        ),
    )
    @settings(max_examples=2)
    def test_combined_property_matches(self, context, ppairs):
        """
        Test for behaviour as observed in #1

        If matching multiple properties, then the result is the union of
        the matching sets, i.e., the resulting filter is a disjunction.
        """
        enumeration = context.list_devices()

        for key, value in ppairs:
            enumeration.match_property(key, value)

        _test_direct_and_complement(
            context,
            frozenset(enumeration),
            lambda d: any(d.properties.get(key) == value for key, value in ppairs),
        )

    @given(
        _CONTEXT_STRATEGY,
        _SUBSYSTEM_STRATEGY,
        _SYSNAME_STRATEGY,
        _MATCH_PROPERTY_STRATEGY,
    )
    @settings(max_examples=10)
    def test_match(self, context, subsystem, sysname, ppair):
        """
        Test that matches from different categories are a conjunction.
        """
        prop_name, prop_value = ppair
        kwargs = {prop_name: prop_value}
        devices = frozenset(
            context.list_devices().match(
                subsystem=subsystem, sys_name=sysname, **kwargs
            )
        )
        _test_direct_and_complement(
            context,
            devices,
            lambda d: d.subsystem == subsystem
            and d.sys_name == sysname
            and d.properties.get(prop_name) == prop_value,
        )


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
        with mock.patch.object(
            enumerator, "match_subsystem", autospec=True
        ) as match_subsystem:
            enumerator.match(subsystem=mock.sentinel.subsystem)
            match_subsystem.assert_called_with(mock.sentinel.subsystem)

    @given(_ENUMERATOR_STRATEGY)
    @settings(max_examples=1)
    def test_match_passthrough_sys_name(self, enumerator):
        """
        Test that special keyword sys_name results in a match_sys_name call.
        """
        with mock.patch.object(
            enumerator, "match_sys_name", autospec=True
        ) as match_sys_name:
            enumerator.match(sys_name=mock.sentinel.sys_name)
            match_sys_name.assert_called_with(mock.sentinel.sys_name)

    @given(_ENUMERATOR_STRATEGY)
    @settings(max_examples=1)
    def test_match_passthrough_tag(self, enumerator):
        """
        Test that special keyword tag results in a match_tag call.
        """
        with mock.patch.object(enumerator, "match_tag", autospec=True) as match_tag:
            enumerator.match(tag=mock.sentinel.tag)
            match_tag.assert_called_with(mock.sentinel.tag)

    @_UDEV_TEST(172, "test_match_passthrough_parent")
    @given(_ENUMERATOR_STRATEGY)
    @settings(max_examples=1)
    def test_match_passthrough_parent(self, enumerator):
        """
        Test that special keyword 'parent' results in a match parent call.
        """
        with mock.patch.object(
            enumerator, "match_parent", autospec=True
        ) as match_parent:
            enumerator.match(parent=mock.sentinel.parent)
            match_parent.assert_called_with(mock.sentinel.parent)

    @given(_ENUMERATOR_STRATEGY)
    @settings(max_examples=1)
    def test_match_passthrough_property(self, enumerator):
        """
        Test that non-special keyword args are treated as properties.
        """
        with mock.patch.object(
            enumerator, "match_property", autospec=True
        ) as match_property:
            enumerator.match(eggs=mock.sentinel.eggs, spam=mock.sentinel.spam)
            assert match_property.call_count == 2
            posargs = [args for args, _ in match_property.call_args_list]
            assert ("spam", mock.sentinel.spam) in posargs
            assert ("eggs", mock.sentinel.eggs) in posargs
