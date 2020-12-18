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
    pyudev.tests.test_device
    ========================

    Test for devices.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

# isort: FUTURE
from __future__ import absolute_import, division, print_function, unicode_literals

# isort: STDLIB
import gc

from ._device_tests._attributes_tests import TestAttributes
from ._device_tests._device_tests import TestDevice
from ._device_tests._devices_tests import TestDevices  # pylint: disable=unused-import
from ._device_tests._tags_tests import TestTags  # pylint: disable=unused-import


def test_garbage():
    """
    Make sure that all the device tests create no uncollectable objects.

    This test must stick at the bottom of this test file to make sure that
    ``py.test`` always executes it at last.
    """
    assert not gc.garbage
