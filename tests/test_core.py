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

# isort: FUTURE
from __future__ import absolute_import, division, print_function, unicode_literals

# isort: STDLIB
import random
import syslog

# isort: THIRDPARTY
from tests._constants import _UDEV_TEST
from tests.utils import is_unicode_string

# isort: LOCAL
from pyudev import udev_version

try:
    from unittest import mock
except ImportError:
    import mock


def test_udev_version():
    assert isinstance(udev_version(), int)
    # just to make sure, that udev versioning works.  pyudev itself should be
    # compatible with earlier versions of pyudev.  However, 150 is currently
    # the earliest udev release, I'm testing against (using Ubuntu 10.04)
    assert udev_version() > 150


class TestContext(object):
    def test_sys_path(self, context):
        assert is_unicode_string(context.sys_path)
        assert context.sys_path == "/sys"

    def test_device_path(self, context):
        assert is_unicode_string(context.device_path)
        assert context.device_path == "/dev"

    @_UDEV_TEST(167, "test_run_path")
    def test_run_path(self, context):
        assert is_unicode_string(context.run_path)
        assert context.run_path == "/run/udev"

    def test_log_priority_get(self, context):
        assert isinstance(context.log_priority, int)
        assert syslog.LOG_EMERG <= context.log_priority <= syslog.LOG_DEBUG

    def test_log_priority_get_mock(self, context):
        spec = lambda c: None
        funcname = "udev_get_log_priority"
        with mock.patch.object(context._libudev, funcname, autospec=spec) as func:
            func.return_value = mock.sentinel.log_priority
            assert context.log_priority is mock.sentinel.log_priority
            func.assert_called_once_with(context)

    def test_log_priority_set_mock(self, context):
        spec = lambda c, p: None
        funcname = "udev_set_log_priority"
        with mock.patch.object(context._libudev, funcname, autospec=spec) as func:
            context.log_priority = mock.sentinel.log_priority
            func.assert_called_once_with(context, mock.sentinel.log_priority)

    def test_log_priority_roundtrip(self, context):
        # FIXME: This adds UDEV_LOG properties?!
        old_priority = context.log_priority
        available_levels = [
            l
            for l in range(syslog.LOG_EMERG, syslog.LOG_DEBUG + 1)
            if l != old_priority
        ]
        new_priority = random.choice(available_levels)
        assert new_priority != old_priority
        try:
            context.log_priority = new_priority
            assert context.log_priority == new_priority
        finally:
            context.log_priority = old_priority
