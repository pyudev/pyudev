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

    _VOLATILE_ATTRIBUTES = ['energy_uj', 'power_on_acct']

    @classmethod
    def non_volatile_items(cls, attributes):
        return ((k, v) for (k, v) in attributes.items() \
           if k not in cls._VOLATILE_ATTRIBUTES)

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=5)
    )
    def test_getitem(self, a_context, device_datum):
        device = Device.from_path(a_context, device_datum.device_path)
        for key, value in self.non_volatile_items(device_datum.attributes):
            raw_value = value.encode(sys.getfilesystemencoding())
            assert isinstance(device.attributes.lookup(key), bytes)
            assert device.attributes.lookup(key) == raw_value

    @given(
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=5)
    )
    def test_getitem_nonexisting(self, a_device):
        assert a_device.attributes.lookup('a non-existing attribute') is None

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=5)
    )
    def test_asstring(self, a_context, device_datum):
        device = Device.from_path(a_context, device_datum.device_path)
        for key, value in self.non_volatile_items(device_datum.attributes):
            assert pytest.is_unicode_string(
                device.attributes.asstring(key))
            assert device.attributes.asstring(key) == value

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=5)
    )
    def test_asint(self, a_context, device_datum):
        device = Device.from_path(a_context, device_datum.device_path)
        for key, value in self.non_volatile_items(device_datum.attributes):
            try:
                value = int(value)
            except ValueError:
                with pytest.raises(ValueError):
                    device.attributes.asint(key)
            else:
                assert device.attributes.asint(key) == value

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=5)
    )
    def test_asbool(self, a_context, device_datum):
        device = Device.from_path(a_context, device_datum.device_path)
        for key, value in self.non_volatile_items(device_datum.attributes):
            if value == '1':
                assert device.attributes.asbool(key)
            elif value == '0':
                assert not device.attributes.asbool(key)
            else:
                with pytest.raises(ValueError) as exc_info:
                    device.attributes.asbool(key)
                message = 'Not a boolean value:'
                assert str(exc_info.value).startswith(message)
