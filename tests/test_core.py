# -*- coding: utf-8 -*-
# Copyright (C) 2010, 2011 Sebastian Wiesner <lunaryorn@googlemail.com>

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

import random
import syslog

import mock
import pytest

from pyudev import udev_version


def test_udev_version():
    assert isinstance(udev_version(), int)
    # just to make sure, that udev versioning works.  pyudev itself should be
    # compatible with earlier versions of pyudev.  However, 150 is currently
    # the earliest udev release, I'm testing against (using Ubuntu 10.04)
    assert udev_version() > 150


class TestContext(object):

    def test_sys_path(self, context):
        assert pytest.is_unicode_string(context.sys_path)
        assert context.sys_path == '/sys'

    def test_device_path(self, context):
        assert pytest.is_unicode_string(context.device_path)
        assert context.device_path == '/dev'

    @pytest.need_udev_version('>= 167')
    def test_run_path(self, context):
        assert pytest.is_unicode_string(context.run_path)
        assert context.run_path == '/run/udev'

    def test_log_priority_get(self, context):
        assert isinstance(context.log_priority, int)
        assert syslog.LOG_EMERG <= context.log_priority <= syslog.LOG_DEBUG

    def test_log_priority_get_mock(self, context):
        get_prio = 'udev_get_log_priority'
        with pytest.patch_libudev(get_prio) as get_prio:
            get_prio.return_value = mock.sentinel.log_priority
            assert context.log_priority is mock.sentinel.log_priority
            get_prio.assert_called_with(context)

    def test_log_priority_set_mock(self, context):
        set_prio = 'udev_set_log_priority'
        with pytest.patch_libudev(set_prio) as set_prio:
            context.log_priority = mock.sentinel.log_priority
            set_prio.assert_called_with(context, mock.sentinel.log_priority)

    def test_log_priority_roundtrip(self, context):
        old_priority = context.log_priority
        available_levels = [
            l for l in range(syslog.LOG_EMERG, syslog.LOG_DEBUG + 1)
            if l != old_priority]
        new_priority = random.choice(available_levels)
        assert new_priority != old_priority
        try:
            context.log_priority = new_priority
            assert context.log_priority == new_priority
        finally:
            context.log_priority = old_priority
