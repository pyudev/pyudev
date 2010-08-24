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

from __future__ import unicode_literals

import sys
import os
import errno

import py.test
from mock import Mock

from pyudev import _util


def test_call_handle_error_return_no_error():
    func = Mock(return_value=0)
    _util.call_handle_error_return(func, 'spam', 'eggs')
    assert func.called_with_args('spam', 'eggs')

def test_call_handle_error_return_memory_error():
    func = Mock(return_value=-errno.ENOMEM)
    with py.test.raises(MemoryError):
        _util.call_handle_error_return(func, 'spam', 'eggs')
    assert func.called_with_args('spam', 'eggs')

def test_call_handle_error_return_environment_error():
    func = Mock(return_value=-errno.ENOENT)
    with py.test.raises(EnvironmentError) as exc_info:
        _util.call_handle_error_return(func, 'spam', 'eggs')
    error = exc_info.value
    assert error.errno == errno.ENOENT
    assert error.strerror == os.strerror(errno.ENOENT)
    assert func.called_with_args('spam', 'eggs')


@py.test.mark.conversion
def test_assert_bytes():
    assert isinstance(_util.assert_bytes('hello world'), bytes)
    assert _util.assert_bytes('hello world') == b'hello world'
    hello = b'hello world'
    assert _util.assert_bytes(hello) is hello


@py.test.mark.conversion
def test_assert_bytes_none():
    with py.test.raises(AttributeError):
        _util.assert_bytes(None)


@py.test.mark.conversion
def test_property_value_to_bytes_string():
    hello = 'hello world'.encode(sys.getfilesystemencoding())
    assert _util.property_value_to_bytes(hello) is hello
    assert isinstance(_util.property_value_to_bytes('hello world'), bytes)
    assert _util.property_value_to_bytes('hello world') == hello


@py.test.mark.conversion
def test_property_value_to_bytes_int():
    assert _util.property_value_to_bytes(10000) == b'10000'
    assert isinstance(_util.property_value_to_bytes(10000), bytes)

@py.test.mark.conversion
def test_property_value_to_bytes_bool():
    assert _util.property_value_to_bytes(True) == b'1'
    assert isinstance(_util.property_value_to_bytes(True), bytes)
    assert _util.property_value_to_bytes(False) == b'0'
    assert isinstance(_util.property_value_to_bytes(False), bytes)
