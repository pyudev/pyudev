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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import stat
import sys

from hypothesis import given
from hypothesis import strategies
from hypothesis import Settings

import pytest

from pyudev import Device

from ..utils import is_unicode_string

from ._device_tests import _CONTEXT_STRATEGY
from ._device_tests import _DEVICE_DATA
from ._device_tests import _DEVICES
from ._device_tests import _UDEV_TEST

class TestAttributes(object):
    """
    Test ``Attributes`` class methods.
    """

    _VOLATILE_ATTRIBUTES = ['energy_uj', 'power_on_acct']

    @classmethod
    def non_volatile_items(cls, attributes):
        """
        Yields keys for non-volatile attributes only.

        :param dict attributes: attributes dict obtained from udev
        """
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
            assert isinstance(device.attributes.get(key), bytes)
            assert device.attributes.get(key) == raw_value

    @given(
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=5)
    )
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

    @given(
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=5)
    )
    def test_non_iterable(self, a_device):
        """
        Test that the attributes object can not be iterated over.
        """
        # pylint: disable=pointless-statement
        with pytest.raises(TypeError):
            'key' in a_device.attributes
        with pytest.raises(TypeError):
            a_device.attributes['key']

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=5)
    )
    def test_asstring(self, a_context, device_datum):
        device = Device.from_path(a_context, device_datum.device_path)
        for key, value in self.non_volatile_items(device_datum.attributes):
            assert is_unicode_string(device.attributes.asstring(key))
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

    @_UDEV_TEST(167, "test_available_attributes")
    @given(
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=5)
    )
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
