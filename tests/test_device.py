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


from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import gc

import pytest

from ._device_tests import _DEVICE_DATA

# pylint: disable=too-few-public-methods

if len(_DEVICE_DATA) > 0:
    # pylint: disable=unused-import
    from ._device_tests._devices_tests import TestDevices
else:
    class TestDevices(object):
        """ Not enough devices available. """

        def test_all(self):
            """ Always skipped test. """
            pytest.skip("skipping all devices tests, not enough devices")

if len(_DEVICE_DATA) > 0:
    # pylint: disable=unused-import
    from ._device_tests._device_tests import TestDevice
else:
    class TestDevice(object):
        """ Not enough devices available. """

        def test_all(self):
            """ Always skipped test. """
            pytest.skip("skipping all device tests, not enough devices")


if len(_DEVICE_DATA) > 0:
    # pylint: disable=unused-import
    from ._device_tests._attributes_tests import TestAttributes
else:
    class TestAttributes(object):
        """ Not enough devices available. """

        def test_all(self):
            """ Always skipped test. """
            pytest.skip("skipping all attributes tests, not enough devices")

if len(_DEVICE_DATA) > 0:
    # pylint: disable=unused-import
    from ._device_tests._tags_tests import TestTags
else:
    class TestTags(object):
        """ Not enough devices available. """

        def test_all(self):
            """ Always skipped test. """
            pytest.skip("skipping all tags tests, not enough devices")


def test_garbage():
    """
    Make sure that all the device tests create no uncollectable objects.

    This test must stick at the bottom of this test file to make sure that
    ``py.test`` always executes it at last.
    """
    assert not gc.garbage
