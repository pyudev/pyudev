# -*- coding: utf-8 -*-
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

import sys

import py.test

import udev


def test__check_call_zero_result():
    assert udev._check_call(lambda x: 0, 'hello') == 0


def test__check_call_nonzero_result():
    py.test.raises(EnvironmentError, udev._check_call, lambda: -1)
    py.test.raises(EnvironmentError, udev._check_call, lambda: 1)
    py.test.raises(EnvironmentError, udev._check_call, lambda: 100)


def test__check_call_invalid_args():
    py.test.raises(TypeError, udev._check_call, lambda x: 0)
    py.test.raises(TypeError, udev._check_call, lambda x: 0, 1, 2, 3)


@py.test.mark.conversion
def test__assert_bytes():
    assert isinstance(udev._assert_bytes(u'hello world'), str)
    assert udev._assert_bytes(u'hello world') == b'hello world'
    hello = b'hello world'
    assert udev._assert_bytes(hello) is hello


@py.test.mark.conversion
def test__assert_bytes_none():
    with py.test.raises(AttributeError):
        udev._assert_bytes(None)


@py.test.mark.conversion
def test__property_value_to_bytes_string():
    hello = u'hello world'.encode(sys.getfilesystemencoding())
    assert udev._property_value_to_bytes(hello) is hello
    assert isinstance(udev._property_value_to_bytes(u'hello world'), str)
    assert udev._property_value_to_bytes(u'hello world') == hello


@py.test.mark.conversion
def test__property_value_to_bytes_int():
    assert udev._property_value_to_bytes(10000) == b'10000'
    assert isinstance(udev._property_value_to_bytes(10000), str)

@py.test.mark.conversion
def test__property_value_to_bytes_bool():
    assert udev._property_value_to_bytes(True) == '1'
    assert isinstance(udev._property_value_to_bytes(True), str)
    assert udev._property_value_to_bytes(False) == '0'
    assert isinstance(udev._property_value_to_bytes(False), str)
