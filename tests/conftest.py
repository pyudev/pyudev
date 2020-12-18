# -*- coding: utf-8 -*-
# Copyright (C) 2010, 2011, 2012, 2013 Sebastian Wiesner <lunaryorn@gmail.com>

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

# isort: FUTURE
from __future__ import absolute_import, division, print_function, unicode_literals

# isort: THIRDPARTY
import pytest

# isort: LOCAL
import pyudev

pytest_plugins = [
    str("tests.plugins.fake_monitor"),
    str("tests.plugins.mock_libudev"),
    str("tests.plugins.travis"),
]


@pytest.fixture
def context(request):
    """
    Return a useable :class:`pyudev.Context` object.
    """
    try:
        return pyudev.Context()
    except ImportError:
        pytest.skip("udev not available")
