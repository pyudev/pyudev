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
    utils.strategies
    =====================

    Strategies for use by the hypothesis python library.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import operator

from hypothesis import strategies

import pyudev

from .udev import DeviceDatabase
from .udev import get_device_sample

context = pyudev.Context()

device_data = get_device_sample(DeviceDatabase.db())

devices = [pyudev.Device.from_path(context, d.device_path) for d in device_data]

CONTEXT_STRATEGY = strategies.just(pyudev.Context())

BLOCK_DEVICES_STRATEGY = strategies.sampled_from(
   context.list_devices(subsystem='block')
)

CHAR_DEVICES_STRATEGY = strategies.sampled_from(
   context.list_devices(subsystem='tty')
)

DEVICES_STRATEGY = strategies.sampled_from(devices)

DEVICE_DATA_STRATEGY = strategies.sampled_from(device_data)

OPERATORS_STRATEGY = strategies.sampled_from(
   [operator.gt, operator.lt, operator.le, operator.ge]
)
