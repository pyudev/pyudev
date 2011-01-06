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

import pytest


from pyudev import udev_version


def test_udev_version():
    assert isinstance(udev_version(), int)
    # just to make sure, that udev versioning works.  pyudev itself should be
    # compatible with earlier versions of pyudev.  However, 150 is currently
    # the earliest udev release, I'm testing against (using Ubuntu 10.04)
    assert udev_version() > 150


def test_context_syspath(context):
    assert pytest.is_unicode_string(context.sys_path)
    assert context.sys_path == '/sys'


def test_context_devpath(context):
    assert pytest.is_unicode_string(context.device_path)
    assert context.device_path == '/dev'
