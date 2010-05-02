# Copyright (c) 2010 Sebastian Wiesner <lunaryorn@googlemail.com>
# Copyright (C) 2010 Sebastian Wiesner <lunaryorn@googlemail.com>

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


import ctypes

import py.test

import _udev


def pytest_funcarg__libudev(request):
    return _udev.load_udev_library()


def pytest_funcarg__context(request):
    libudev = request.getfuncargvalue('libudev')
    context = libudev.udev_new()
    request.addfinalizer(lambda: libudev.udev_unref(context))
    return context


def _assert_path(context, func, expected):
    py.test.raises(TypeError, func)
    py.test.raises(ctypes.ArgumentError, func, 'foo')
    path = func(context)
    assert isinstance(path, str)
    assert expected == expected


def test_get_sys_path(libudev, context):
    _assert_path(context, libudev.udev_get_sys_path, '/sys')


def test_get_dev_path(libudev, context):
    _assert_path(context, libudev.udev_get_dev_path, '/dev')

