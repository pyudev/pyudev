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

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import sys
import errno

import pytest
from mock import Mock

from pyudev import _util


@pytest.mark.conversion
def test_ensure_byte_string():
    assert isinstance(_util.ensure_byte_string('hello world'), bytes)
    assert _util.ensure_byte_string('hello world') == b'hello world'
    hello = b'hello world'
    assert _util.ensure_byte_string(hello) is hello


@pytest.mark.conversion
def test_ensure_byte_string_none():
    with pytest.raises(AttributeError):
        _util.ensure_byte_string(None)


@pytest.mark.conversion
def test_ensure_unicode_string():
    assert pytest.is_unicode_string(
        _util.ensure_unicode_string(b'hello world'))
    assert _util.ensure_unicode_string(b'hello world') == 'hello world'
    hello = 'hello world'
    assert _util.ensure_unicode_string(hello) is hello


@pytest.mark.conversion
def test_ensure_unicode_string_none():
    with pytest.raises(AttributeError):
        _util.ensure_unicode_string(None)


@pytest.mark.conversion
def test_property_value_to_bytes_string():
    hello = 'hello world'.encode(sys.getfilesystemencoding())
    assert _util.property_value_to_bytes(hello) is hello
    assert isinstance(_util.property_value_to_bytes('hello world'), bytes)
    assert _util.property_value_to_bytes('hello world') == hello


@pytest.mark.conversion
def test_property_value_to_bytes_int():
    assert _util.property_value_to_bytes(10000) == b'10000'
    assert isinstance(_util.property_value_to_bytes(10000), bytes)


@pytest.mark.conversion
def test_property_value_to_bytes_bool():
    assert _util.property_value_to_bytes(True) == b'1'
    assert isinstance(_util.property_value_to_bytes(True), bytes)
    assert _util.property_value_to_bytes(False) == b'0'
    assert isinstance(_util.property_value_to_bytes(False), bytes)


@pytest.mark.conversion
def test_string_to_bool_true():
    assert isinstance(_util.string_to_bool('1'), bool)
    assert _util.string_to_bool('1')


@pytest.mark.conversion
def test_string_to_bool_false():
    assert isinstance(_util.string_to_bool('0'), bool)
    assert not _util.string_to_bool('0')


@pytest.mark.conversion
def test_string_to_bool_invalid_value():
    with pytest.raises(ValueError) as exc_info:
        _util.string_to_bool('foo')
    assert str(exc_info.value) == 'Not a boolean value: {0!r}'.format('foo')


def test_udev_list_iterate_no_entry():
    assert not list(_util.udev_list_iterate(Mock(), None))


def test_udev_list_iterate_mock():
    libudev = Mock(name='libudev')
    items = [('spam', 'eggs'), ('foo', 'bar')]
    with pytest.libudev_list(libudev, 'udev_enumerate_get_list_entry', items):
        udev_list = libudev.udev_enumerate_get_list_entry()
        assert list(_util.udev_list_iterate(libudev, udev_list)) == [
            ('spam', 'eggs'), ('foo', 'bar')]


def raise_valueerror():
    raise ValueError('from function')


def test_get_device_type_character_device():
    assert _util.get_device_type('/dev/console') == 'char'


def test_get_device_type_block_device():
    try:
        assert _util.get_device_type('/dev/sda') == 'block'
    except EnvironmentError:
        pytest.skip('device node not found')


def test_get_device_type_no_device_file(tmpdir):
    filename = tmpdir.join('test')
    filename.ensure(file=True)
    with pytest.raises(ValueError) as excinfo:
        _util.get_device_type(str(filename))
    message = 'not a device file: {0!r}'.format(str(filename))
    assert str(excinfo.value) == message


def test_get_device_type_not_existing(tmpdir):
    filename = tmpdir.join('test')
    assert not tmpdir.check(file=True)
    with pytest.raises(EnvironmentError) as excinfo:
        _util.get_device_type(str(filename))
    pytest.assert_env_error(excinfo.value, errno.ENOENT, str(filename))


def test_eintr_retry_call(tmpdir):
    import os, signal, select

    def handle_alarm(signum, frame):
        pass
    orig_alarm = signal.getsignal(signal.SIGALRM)

    # Open an empty file and use it to wait for exceptions which should
    # never happen
    filename = tmpdir.join('test')
    filename.ensure(file=True)
    fd = os.open(str(filename), os.O_RDONLY)

    try:
        signal.signal(signal.SIGALRM, handle_alarm)

        # Ensure that a signal raises EINTR on Python < 3.5
        if sys.version_info < (3,5):
            with pytest.raises(select.error) as e:
                signal.alarm(1)
                select.select([], [], [fd], 2)

        # Ensure that wrapping the call does not raise EINTR
        signal.alarm(1)
        assert _util.eintr_retry_call(select.select, [], [], [3], 2) == ([], [], [])
    finally:
        os.close(fd)
        signal.signal(signal.SIGALRM, orig_alarm)
