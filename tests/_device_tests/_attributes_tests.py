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


class TestAttributes:
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
        for key in device_datum.attributes.keys():
            value = device.attributes.get(key)
            if value is not None:
                assert isinstance(value, bytes)

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
        for key in device_datum.attributes.keys():
            try:
                assert is_unicode_string(device.attributes.asstring(key))
            except KeyError:
                pass

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
                try:
                    device.attributes.asint(key)
                except KeyError:
                    pass
                except ValueError:
                    pass

    @given(_CONTEXT_STRATEGY, strategies.sampled_from(_DEVICE_DATA))
    @settings(max_examples=5)
    def test_asbool(self, a_context, device_datum):
        """
        Test that bool result is a bool or ValueError raised.
        """
        device = Devices.from_path(a_context, device_datum.device_path)
        for key, value in device_datum.attributes.items():
            if value in ("0", "1"):
                try:
                    assert device.attributes.asbool(key) in (False, True)
                except KeyError:
                    pass
            else:
                try:
                    device.attributes.asbool(key)
                except KeyError:
                    pass
                except ValueError:
                    pass
