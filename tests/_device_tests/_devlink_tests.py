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
Tests methods belonging to Devlink class.

.. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from itertools import groupby

from hypothesis import given
from hypothesis import strategies
from hypothesis import Settings

import pytest

from pyudev import Devlink

from .._constants import _DEVICES


class TestDevlinks(object):
    """
    Test ``Devlinks`` methods.
    """
    # pylint: disable=too-few-public-methods

    _devices = [d for d in _DEVICES if list(d.device_links)]
    if len(_devices) > 0:
        @given(
           strategies.sampled_from(_devices),
           settings=Settings(max_examples=5)
        )
        def test_devlinks(self, a_device):
            """
            Verify that device links are in "by-.*" categories or no category.
            """
            device_links = (Devlink(d) for d in a_device.device_links)

            def sort_func(dl):
                """
                :returns: category of device link
                :rtype: str
                """
                key = dl.category
                return key if key is not None else ""

            devlinks = sorted(device_links, key=sort_func)

            categories = list(k for k, g in groupby(devlinks, sort_func))
            assert all(c == "" or c.startswith("by-") for c in categories)

            assert all((d.category is None and d.value is None) or \
               (d.category is not None and d.value is not None) \
               for d in devlinks)

            assert all(d.path == str(d) for d in devlinks)
    else:
        def test_devlinks(self):
            # pylint: disable=missing-docstring
            pytest.skip("not enough devices with devlinks")
