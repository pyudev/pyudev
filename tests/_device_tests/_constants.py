# -*- coding: utf-8 -*-
# Copyright (C) 2015 mulhern <amulhern@redhat.com>

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
    pyudev.tests._device_tests
    ==========================

    Tests for devices.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from hypothesis import strategies

import pytest

from pyudev import Context
from pyudev import Device

from ..utils import udev

_CONTEXT = Context()
_DEVICE_DATA = list(udev.get_device_sample(udev.DeviceDatabase.db()))
_DEVICES = [Device.from_path(_CONTEXT, d.device_path) for d in _DEVICE_DATA]

_CONTEXT_STRATEGY = strategies.just(_CONTEXT)

_UDEV_VERSION = int(udev.UDevAdm.adm().query_udev_version())

def _UDEV_TEST(version, node=None): # pylint: disable=invalid-name
    fmt_str = "%s: udev version must be at least %s, is %s"
    return pytest.mark.skipif(
       _UDEV_VERSION < version,
       reason=fmt_str % (node, version, _UDEV_VERSION)
    )
