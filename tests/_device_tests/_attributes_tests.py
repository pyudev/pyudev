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

import sys
from itertools import count

from hypothesis import given
from hypothesis import strategies
from hypothesis import Settings

import pytest

from pyudev import Device

from ._device_tests import _CONTEXT_STRATEGY
from ._device_tests import _DEVICE_DATA
from ._device_tests import _DEVICES
from ._device_tests import _UDEV_TEST

class TestAttributes(object):

    @given(
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=5)
    )
    def test_length(self, a_device):
        counter = count()
        for _ in a_device.attributes:
            next(counter)
        assert len(a_device.attributes) == next(counter)

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=5)
    )
    def test_iteration(self, a_context, device_datum):
        device = Device.from_path(a_context, device_datum.device_path)
        for attribute in device.attributes:
            assert pytest.is_unicode_string(attribute)
        # check that iteration really yields all attributes
        device_attributes = set(device.attributes)
        for attribute in device_datum.attributes:
            assert attribute in device_attributes

    @_UDEV_TEST(167, "test_iteration_mock")
    @given(
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=5)
    )
    def test_iteration_mock(self, a_device):
        attributes = [b'spam', b'eggs']
        funcname = 'udev_device_get_sysattr_list_entry'
        with pytest.libudev_list(a_device._libudev, funcname, attributes):
            attrs = list(a_device.attributes)
            assert attrs == ['spam', 'eggs']
            func = a_device._libudev.udev_device_get_sysattr_list_entry
            func.assert_called_with(a_device)

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=5)
    )
    def test_contains(self, a_context, device_datum):
        device = Device.from_path(a_context, device_datum.device_path)
        for attribute in device_datum.attributes:
            assert attribute in device.attributes

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=5)
    )
    def test_getitem(self, a_context, device_datum):
        device = Device.from_path(a_context, device_datum.device_path)
        for attribute, value in device_datum.attributes.items():
            raw_value = value.encode(sys.getfilesystemencoding())
            assert isinstance(device.attributes[attribute], bytes)
            assert device.attributes[attribute] == raw_value

    @given(
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=5)
    )
    def test_getitem_nonexisting(self, a_device):
        with pytest.raises(KeyError) as excinfo:
            # pylint: disable=pointless-statement
            a_device.attributes['a non-existing attribute']
        assert str(excinfo.value) == repr('a non-existing attribute')

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=5)
    )
    def test_asstring(self, a_context, device_datum):
        device = Device.from_path(a_context, device_datum.device_path)
        for attribute, value in device_datum.attributes.items():
            assert pytest.is_unicode_string(
                device.attributes.asstring(attribute))
            assert device.attributes.asstring(attribute) == value

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=5)
    )
    def test_asint(self, a_context, device_datum):
        device = Device.from_path(a_context, device_datum.device_path)
        for attribute, value in device_datum.attributes.items():
            try:
                value = int(value)
            except ValueError:
                with pytest.raises(ValueError):
                    device.attributes.asint(attribute)
            else:
                assert device.attributes.asint(attribute) == value

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=5)
    )
    def test_asbool(self, a_context, device_datum):
        device = Device.from_path(a_context, device_datum.device_path)
        for attribute, value in device_datum.attributes.items():
            if value == '1':
                assert device.attributes.asbool(attribute)
            elif value == '0':
                assert not device.attributes.asbool(attribute)
            else:
                with pytest.raises(ValueError) as exc_info:
                    device.attributes.asbool(attribute)
                message = 'Not a boolean value:'
                assert str(exc_info.value).startswith(message)
