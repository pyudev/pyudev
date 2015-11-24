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

from hypothesis import given
from hypothesis import strategies
from hypothesis import Settings

import pytest
import mock

from pyudev import Device

from ._device_tests import _CONTEXT_STRATEGY
from ._device_tests import _DEVICE_DATA
from ._device_tests import _DEVICES
from ._device_tests import _UDEV_TEST

class TestTags(object):

    pytestmark = _UDEV_TEST(154, "TestTags")

    _device_data = [d for d in _DEVICE_DATA if d.tags]
    if len(_device_data) > 0:
        @given(
           _CONTEXT_STRATEGY,
           strategies.sampled_from(_device_data),
           settings=Settings(max_examples=5)
        )
        def test_iteration(self, a_context, device_datum):
            device = Device.from_path(a_context, device_datum.device_path)
            assert set(device.tags) == set(device_datum.tags)
            for tag in device.tags:
                assert pytest.is_unicode_string(tag)

        @given(
           _CONTEXT_STRATEGY,
           strategies.sampled_from(_device_data),
           settings=Settings(max_examples=5)
        )
        def test_contains(self, a_context, device_datum):
            device = Device.from_path(a_context, device_datum.device_path)
            for tag in device_datum.tags:
                assert tag in device.tags
    else:
        def test_iteration(self):
            pytest.skip("not enough devices with tags")

        def test_contains(self):
            pytest.skip("not enough devices with tags")

    @given(
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=5)
    )
    def test_iteration_mock(self, a_device):
        funcname = 'udev_device_get_tags_list_entry'
        with pytest.libudev_list(a_device._libudev, funcname,
                                 [b'spam', b'eggs']):
            tags = list(a_device.tags)
            assert tags == ['spam', 'eggs']
            func = a_device._libudev.udev_device_get_tags_list_entry
            func.assert_called_once_with(a_device)


    @_UDEV_TEST(172, "test_contans_mock")
    @given(
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=5)
    )
    def test_contains_mock(self, a_device):
        """
        Test that ``udev_device_has_tag`` is called if available.
        """
        funcname = 'udev_device_has_tag'
        spec = lambda d, t: None
        with mock.patch.object(a_device._libudev, funcname,
                               autospec=spec) as func:
            func.return_value = 1
            assert 'foo' in a_device.tags
            func.assert_called_once_with(a_device, b'foo')
