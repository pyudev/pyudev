# -*- coding: utf-8 -*-
# Copyright (C) 2015 Anne Mulhern <amulhern@redhat.com>

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
"""
    tests.test_discover
    ===================

    Tests discovering what device is meant by somewhat unspecific information.

    .. moduleauthor:: mulhern <amulhern@redhat.com>
"""

# isort: FUTURE
from __future__ import absolute_import, division, print_function, unicode_literals

# isort: STDLIB
import os

# isort: THIRDPARTY
import pytest
from hypothesis import assume, given, settings, strategies

# isort: LOCAL
import pyudev
from pyudev import (
    DeviceFileHypothesis,
    DeviceNameHypothesis,
    DeviceNumberHypothesis,
    DevicePathHypothesis,
    Discovery,
)

_CONTEXT = pyudev.Context()
_DEVICES = [d for d in _CONTEXT.list_devices()]

NUM_TESTS = 5


class TestUtilities(object):
    """
    Some utilities used by the actual tests.
    """

    @staticmethod
    def get_device_numbers(a_device, a_string):
        """
        Get the device number from the device in a few formats.

        :param :class:`Device` a_device: the device
        :param  str a_string: a likely string between the major and minor
        :returns: a tuple of device numbers
        :rtype: tuple of str
        """
        device_number = a_device.device_number
        major_number = os.major(device_number)
        minor_number = os.minor(device_number)
        pair_number = "%s%s%s" % (major_number, a_string, minor_number)
        return (str(device_number), pair_number)

    @staticmethod
    def get_paths(a_device):
        """
        Get some variants on a device path.

        :param :class:`Device` a_device: the device
        :returns: a tuple of paths in sysfs
        :rtype: tuple of str
        """
        sys_path = a_device.sys_path
        (_, _, truncated_path) = sys_path[1:].partition("/")
        return (sys_path, truncated_path, a_device.device_path)

    @staticmethod
    def get_files(a_device):
        """
        Get a bunch of files, including device nodes and links.

        :param :class:`Device` a_device: the device
        :returns: a list of files
        :rtype: list of str
        """
        links = list(a_device.device_links)
        names = [os.path.basename(l) for l in links]
        links.extend(names)

        device_node = a_device.device_node
        if device_node:
            links.append(device_node)
        return links


class TestDiscovery(object):
    """
    Test discovery of an object from limited bits of its description.
    """

    _CONTEXT = pyudev.Context()
    _DISCOVER = Discovery()
    _DISCOVER.setup(_CONTEXT)

    @given(
        strategies.sampled_from(_DEVICES).filter(lambda x: x.device_number),
        strategies.text(":, -/+=").filter(lambda x: x),
    )
    @settings(max_examples=NUM_TESTS)
    def test_device_number(self, a_device, a_string):
        """
        Test lookup by a device number.

        Note that device number is per class, so there may be two
        devices with the same device number.
        """
        for number in TestUtilities.get_device_numbers(a_device, a_string):
            res = DeviceNumberHypothesis.get_devices(self._CONTEXT, number)
            assert a_device in res

    @given(strategies.sampled_from(_DEVICES))
    @settings(max_examples=NUM_TESTS)
    def test_path(self, a_device):
        """
        Test lookup by path.
        """
        for path in TestUtilities.get_paths(a_device):
            res = DevicePathHypothesis.get_devices(self._CONTEXT, path)
            assert res == set((a_device,))

    @given(strategies.sampled_from(_DEVICES))
    @settings(max_examples=NUM_TESTS)
    def test_name(self, a_device):
        """
        Test lookup by device name.

        Note that there may be multiple devices corresponding to the name
        in different subsystems.
        """
        name = a_device.sys_name
        res = DeviceNameHypothesis.get_devices(self._CONTEXT, name)
        assert a_device in res

    _devices = [d for d in _DEVICES if list(d.device_links)]

    @given(
        strategies.sampled_from(_DEVICES),
        strategies.text(":, -/+=").filter(lambda x: x),
    )
    @settings(max_examples=NUM_TESTS)
    def test_anything(self, a_device, a_string):
        """
        Grab any of the likely candidates for looking up a device.
        """
        assume(not "DM_MULTIPATH_TIMESTAMP" in a_device.properties)

        values = list(TestUtilities.get_device_numbers(a_device, a_string))
        values.extend(TestUtilities.get_paths(a_device))
        values.append(a_device.sys_name)
        values.extend(TestUtilities.get_files(a_device))

        results = frozenset(
            d for v in values for d in self._DISCOVER.get_devices(self._CONTEXT, v)
        )

        assert a_device in results
