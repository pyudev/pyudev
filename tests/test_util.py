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
import sys

# isort: THIRDPARTY
import pytest
from hypothesis import given, settings, strategies

# isort: LOCAL
from pyudev import Context, _util

from .utils import is_unicode_string

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


_CONTEXT = Context()


@pytest.mark.conversion
def test_ensure_byte_string():
    assert isinstance(_util.ensure_byte_string("hello world"), bytes)
    assert _util.ensure_byte_string("hello world") == b"hello world"
    hello = b"hello world"
    assert _util.ensure_byte_string(hello) is hello


@pytest.mark.conversion
def test_ensure_byte_string_none():
    with pytest.raises(AttributeError):
        _util.ensure_byte_string(None)


@pytest.mark.conversion
def test_ensure_unicode_string():
    assert is_unicode_string(_util.ensure_unicode_string(b"hello world"))
    assert _util.ensure_unicode_string(b"hello world") == "hello world"
    hello = "hello world"
    assert _util.ensure_unicode_string(hello) is hello


@pytest.mark.conversion
def test_ensure_unicode_string_none():
    with pytest.raises(AttributeError):
        _util.ensure_unicode_string(None)


@pytest.mark.conversion
def test_property_value_to_bytes_string():
    hello = "hello world".encode(sys.getfilesystemencoding())
    assert _util.property_value_to_bytes(hello) is hello
    assert isinstance(_util.property_value_to_bytes("hello world"), bytes)
    assert _util.property_value_to_bytes("hello world") == hello


@pytest.mark.conversion
def test_property_value_to_bytes_int():
    assert _util.property_value_to_bytes(10000) == b"10000"
    assert isinstance(_util.property_value_to_bytes(10000), bytes)


@pytest.mark.conversion
def test_property_value_to_bytes_bool():
    assert _util.property_value_to_bytes(True) == b"1"
    assert isinstance(_util.property_value_to_bytes(True), bytes)
    assert _util.property_value_to_bytes(False) == b"0"
    assert isinstance(_util.property_value_to_bytes(False), bytes)


@pytest.mark.conversion
def test_string_to_bool_true():
    assert isinstance(_util.string_to_bool("1"), bool)
    assert _util.string_to_bool("1")


@pytest.mark.conversion
def test_string_to_bool_false():
    assert isinstance(_util.string_to_bool("0"), bool)
    assert not _util.string_to_bool("0")


@pytest.mark.conversion
def test_string_to_bool_invalid_value():
    with pytest.raises(ValueError) as exc_info:
        _util.string_to_bool("foo")
    assert str(exc_info.value) == "Not a boolean value: {0!r}".format("foo")


def test_udev_list_iterate_no_entry():
    assert not list(_util.udev_list_iterate(Mock(), None))


def test_udev_list_iterate_mock():
    libudev = Mock(name="libudev")
    items = [("spam", "eggs"), ("foo", "bar")]
    with pytest.libudev_list(libudev, "udev_enumerate_get_list_entry", items):
        udev_list = libudev.udev_enumerate_get_list_entry()
        assert list(_util.udev_list_iterate(libudev, udev_list)) == [
            ("spam", "eggs"),
            ("foo", "bar"),
        ]


def raise_valueerror():
    raise ValueError("from function")


_CHAR_DEVICES = list(_CONTEXT.list_devices(subsystem="tty"))


@pytest.mark.skipif(len(_CHAR_DEVICES) == 0, reason="no tty devices")
@given(strategies.sampled_from(_CHAR_DEVICES))
@settings(max_examples=5)
def test_get_device_type_character_device(a_device):
    """
    Check that the device type of a character device is actually char.
    """
    assert _util.get_device_type(a_device.device_node) == "char"


_BLOCK_DEVICES = list(_CONTEXT.list_devices(subsystem="block"))


@pytest.mark.skipif(len(_BLOCK_DEVICES) == 0, reason="no block devices")
@given(strategies.sampled_from(_BLOCK_DEVICES))
@settings(max_examples=5)
def test_get_device_type_block_device(a_device):
    """
    Check that the device type of a block device is actually block.
    """
    assert _util.get_device_type(a_device.device_node) == "block"


def test_get_device_type_no_device_file(tmpdir):
    filename = tmpdir.join("test")
    filename.ensure(file=True)
    with pytest.raises(ValueError) as excinfo:
        _util.get_device_type(str(filename))
    message = "not a device file: {0!r}".format(str(filename))
    assert str(excinfo.value) == message


def test_get_device_type_not_existing(tmpdir):
    """
    Test that an OSError is raised when checking device type using a file
    that does not actually exist.
    """
    filename = tmpdir.join("test_get_device_type_not_existing")
    assert not tmpdir.check(file=True)
    with pytest.raises(OSError):
        _util.get_device_type(str(filename))


def test_eintr_retry_call(tmpdir):
    import os, signal, select

    def handle_alarm(signum, frame):
        # pylint: disable=unused-argument
        pass

    orig_alarm = signal.getsignal(signal.SIGALRM)

    # Open an empty file and use it to wait for exceptions which should
    # never happen
    filename = tmpdir.join("test")
    filename.ensure(file=True)
    fd = os.open(str(filename), os.O_RDONLY)

    try:
        signal.signal(signal.SIGALRM, handle_alarm)

        # Ensure that a signal raises EINTR on Python < 3.5
        if sys.version_info < (3, 5):
            with pytest.raises(select.error):
                signal.alarm(1)
                select.select([], [], [fd], 2)

        # Ensure that wrapping the call does not raise EINTR
        signal.alarm(1)
        assert _util.eintr_retry_call(select.select, [], [], [3], 2) == ([], [], [])
    finally:
        os.close(fd)
        signal.signal(signal.SIGALRM, orig_alarm)
