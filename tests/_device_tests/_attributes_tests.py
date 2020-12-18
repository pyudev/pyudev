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
"""
Tests methods belonging to Attributes class.

.. moduleauthor::  mulhern <amulhern@redhat.com>
"""

# isort: FUTURE
from __future__ import absolute_import, division, print_function, unicode_literals

# isort: STDLIB
import os
import stat

# isort: THIRDPARTY
import pytest
from hypothesis import given, settings, strategies

# isort: LOCAL
from pyudev import Devices

from ..utils import is_unicode_string
from ._device_tests import _CONTEXT_STRATEGY, _DEVICE_DATA, _DEVICES, _UDEV_TEST


class TestAttributes(object):
    """
    Test ``Attributes`` class methods.
    """

    @given(_CONTEXT_STRATEGY, strategies.sampled_from(_DEVICE_DATA))
    @settings(max_examples=5)
    def test_getitem(self, a_context, device_datum):
        """
        Test that attribute value exists and is instance of bytes.
        """
        device = Devices.from_path(a_context, device_datum.device_path)
        assert all(
            isinstance(device.attributes.get(key), bytes)
            for key in device_datum.attributes.keys()
        )

    @given(strategies.sampled_from(_DEVICES))
    @settings(max_examples=5)
    def test_getitem_nonexisting(self, a_device):
        """
        Test behavior when corresponding value is non-existant.
        """
        not_key = "a non-existing attribute"
        assert a_device.attributes.get(not_key) is None
        with pytest.raises(KeyError):
            a_device.attributes.asstring(not_key)
        with pytest.raises(KeyError):
            a_device.attributes.asint(not_key)
        with pytest.raises(KeyError):
            a_device.attributes.asbool(not_key)

    @given(strategies.sampled_from(_DEVICES))
    @settings(max_examples=5)
    def test_non_iterable(self, a_device):
        """
        Test that the attributes object can not be iterated over.
        """
        # pylint: disable=pointless-statement
        with pytest.raises(TypeError):
            "key" in a_device.attributes
        with pytest.raises(TypeError):
            a_device.attributes["key"]

    @given(_CONTEXT_STRATEGY, strategies.sampled_from(_DEVICE_DATA))
    @settings(max_examples=5)
    def test_asstring(self, a_context, device_datum):
        """
        Test that attribute exists for actual device and is unicode.
        """
        device = Devices.from_path(a_context, device_datum.device_path)
        assert all(
            is_unicode_string(device.attributes.asstring(key))
            for key in device_datum.attributes.keys()
        )

    @given(_CONTEXT_STRATEGY, strategies.sampled_from(_DEVICE_DATA))
    @settings(max_examples=10)
    def test_asint(self, a_context, device_datum):
        """
        Test that integer result is an int or ValueError raised.
        """
        device = Devices.from_path(a_context, device_datum.device_path)
        for key, value in device_datum.attributes.items():
            try:
                value = int(value)
            except ValueError:
                with pytest.raises(ValueError):
                    device.attributes.asint(key)

    @given(_CONTEXT_STRATEGY, strategies.sampled_from(_DEVICE_DATA))
    @settings(max_examples=5)
    def test_asbool(self, a_context, device_datum):
        """
        Test that bool result is a bool or ValueError raised.
        """
        device = Devices.from_path(a_context, device_datum.device_path)
        for key, value in device_datum.attributes.items():
            if value in ("0", "1"):
                assert device.attributes.asbool(key) in (False, True)
            else:
                with pytest.raises(ValueError):
                    device.attributes.asbool(key)

    @_UDEV_TEST(167, "test_available_attributes")
    @given(strategies.sampled_from(_DEVICES))
    @settings(max_examples=5)
    def test_available_attributes(self, a_device):
        """
        Test that the available attributes are exactly the names of files
        in the sysfs directory that are regular files or softlinks.
        """
        available_attributes = sorted(a_device.attributes.available_attributes)

        attribute_filenames = []
        sys_path = a_device.sys_path
        for filename in sorted(os.listdir(sys_path)):
            filepath = os.path.join(sys_path, filename)
            status = os.lstat(filepath)
            mode = status.st_mode
            if not stat.S_ISLNK(mode) and not stat.S_ISREG(mode):
                continue
            if not stat.S_IRUSR & mode:
                continue
            attribute_filenames.append(filename)

        assert available_attributes == attribute_filenames
