# -*- coding: utf-8 -*-
# Copyright (C) 2026 Nikolay Plastinin <plaztininikolai@gmail.com>

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
Tests for the ctypes error checkers.
"""

import errno

import pytest

from pyudev._ctypeslib import _errorcheckers


def test_negative_errorcode_or_errno_success(monkeypatch):
    """
    A return value of ``0`` is success, even if ``errno`` is set.
    """
    monkeypatch.setattr(_errorcheckers, "get_errno", lambda: errno.ENOENT)
    assert _errorcheckers.check_negative_errorcode_or_errno(0, None) == 0


def test_negative_errorcode_or_errno_ignores_stale_errno(monkeypatch):
    """
    A negative error code is raised, ignoring an ``errno`` left over from an
    earlier call.
    """
    monkeypatch.setattr(_errorcheckers, "get_errno", lambda: errno.ENOENT)
    with pytest.raises(OSError) as excinfo:
        _errorcheckers.check_negative_errorcode_or_errno(-errno.E2BIG, None)
    assert excinfo.value.errno == errno.E2BIG


def test_negative_errorcode_or_errno_old_udev(monkeypatch):
    """
    A return value of ``-1`` is raised with the ``errno`` set by the function,
    as returned by old versions of udev.
    """
    monkeypatch.setattr(_errorcheckers, "get_errno", lambda: errno.EBUSY)
    with pytest.raises(OSError) as excinfo:
        _errorcheckers.check_negative_errorcode_or_errno(-1, None)
    assert excinfo.value.errno == errno.EBUSY


def test_negative_errorcode_or_errno_eperm(monkeypatch):
    """
    A negative error code is raised, if the function did not set ``errno``.
    """
    monkeypatch.setattr(_errorcheckers, "get_errno", lambda: 0)
    with pytest.raises(OSError) as excinfo:
        _errorcheckers.check_negative_errorcode_or_errno(-errno.EPERM, None)
    assert excinfo.value.errno == errno.EPERM


def test_negative_errorcode_or_errno_mapped_exception(monkeypatch):
    """
    A negative error code with a mapped exception raises that exception.
    """
    monkeypatch.setattr(_errorcheckers, "get_errno", lambda: 0)
    with pytest.raises(ValueError):
        _errorcheckers.check_negative_errorcode_or_errno(-errno.EINVAL, None)
