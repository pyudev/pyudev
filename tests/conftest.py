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

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import os
import sys

import pytest

import pyudev


pytest_plugins = [
    str('tests.plugins.fake_monitor'),
    str('tests.plugins.privileged'),
    str('tests.plugins.mock_libudev'),
    str('tests.plugins.travis'),
]


def assert_env_error(error, errno, filename=None):
    __tracebackhide__ = True
    # work around an apparent limitation in pytest.raises, which gives use
    # tuple representations of exceptions instead of exception objects.  See
    # pyudev issue #43
    if isinstance(error, tuple):
        error = OSError(*error)
    assert error.errno == errno
    assert error.strerror == os.strerror(errno)
    assert error.filename == filename


def is_unicode_string(value):
    """
    Return ``True``, if ``value`` is of a real unicode string type
    (``unicode`` in python 2, ``str`` in python 3), ``False`` otherwise.
    """
    if sys.version_info[0] >= 3:
        unicode_type = str
    else:
        unicode_type = unicode
    return isinstance(value, unicode_type)


def pytest_namespace():
    return dict((func.__name__, func) for func in
                (is_unicode_string, assert_env_error))

@pytest.fixture
def context(request):
    """
    Return a useable :class:`pyudev.Context` object.
    """
    try:
        return pyudev.Context()
    except ImportError:
        pytest.skip('udev not available')
