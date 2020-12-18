# -*- coding: utf-8 -*-
# Copyright (C) 2013 Sebastian Wiesner <lunaryorn@gmail.com>

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
    plugins.travis
    ==============

    Support for Travis CI.
"""

# isort: STDLIB
import os

# isort: THIRDPARTY
import pytest


def is_on_travis_ci():
    """Determine whether the tests run on Travis CI.

    Return ``True``, if so, or ``False`` otherwise.

    """
    return os.environ.get("TRAVIS", "") == "true"


EXPOSED_FUNCTIONS = [is_on_travis_ci]


def pytest_configure():
    for f in EXPOSED_FUNCTIONS:
        setattr(pytest, f.__name__, f)


def pytest_runtest_setup(item):
    if not hasattr(item, "obj"):
        return
    marker = getattr(item.obj, "not_on_travis", None)
    if marker and is_on_travis_ci():
        pytest.skip("Test must not run on Travis CI")
