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

import sys
import os
import socket
import errno
from contextlib import nested

import pytest
import mock

from pyudev import Monitor, Device

# many tests just consist of some monkey patching to test, that the Monitor
# class actually calls out to udev, correctly passing arguments and handling
# return value.  Actual udev calls are difficult to test, as return values
# and side effects are dynamic and environment-dependent.  It isn't
# necessary anyway, libudev can just assumed to be correct.


def test_from_netlink_invalid_source(context):
    with pytest.raises(ValueError) as exc_info:
        Monitor.from_netlink(context, source='invalid_source')
    message = ('Invalid source: {0!r}. Must be one of "udev" '
               'or "kernel"'.format('invalid_source'))
    assert str(exc_info.value) == message


def _assert_from_netlink_called(context, *args):
    new_from_netlink = 'udev_monitor_new_from_netlink'
    with pytest.patch_libudev(new_from_netlink) as new_from_netlink:
        source = args[0].encode('ascii') if args else b'udev'
        new_from_netlink.return_value = mock.sentinel.pointer
        monitor = Monitor.from_netlink(context, *args)
        new_from_netlink.assert_called_with(context._context, source)
        assert isinstance(new_from_netlink.call_args[0][1], bytes)
        assert monitor._monitor is mock.sentinel.pointer


def test_from_netlink_source_udev(context):
    monitor = Monitor.from_netlink(context)
    assert monitor._monitor
    monitor = Monitor.from_netlink(context, source='udev')
    assert monitor._monitor


def test_from_netlink_source_udev_mock(context):
    _assert_from_netlink_called(context)
    _assert_from_netlink_called(context, 'udev')


def test_from_netlink_source_kernel(context):
    monitor = Monitor.from_netlink(context, source='kernel')
    assert monitor._monitor


def test_from_netlink_source_kernel_mock(context):
    _assert_from_netlink_called(context, 'kernel')


def test_from_socket(context, socket_path):
    monitor = Monitor.from_socket(context, str(socket_path))
    assert monitor._monitor


def test_from_socket_mock(context, socket_path):
    socket_path = str(socket_path)
    new_from_socket = 'udev_monitor_new_from_socket'
    with pytest.patch_libudev(new_from_socket) as new_from_socket:
        new_from_socket.return_value = mock.sentinel.pointer
        monitor = Monitor.from_socket(context, socket_path)
        new_from_socket.assert_called_with(
            context._context, socket_path.encode(sys.getfilesystemencoding()))
        assert monitor._monitor is mock.sentinel.pointer
        Monitor.from_socket(context, 'foobar')
        new_from_socket.assert_called_with(context._context, b'foobar')
        assert isinstance(new_from_socket.call_args[0][1], bytes)


def test_fileno(monitor):
    # we can't do more than check that no exception is thrown
    monitor.fileno()


def test_fileno_mock(monitor):
    get_fd = 'udev_monitor_get_fd'
    with pytest.patch_libudev(get_fd) as get_fd:
        get_fd.return_value = mock.sentinel.fileno
        assert monitor.fileno() is mock.sentinel.fileno
        get_fd.assert_called_with(monitor._monitor)


def test_filter_by_no_subsystem(monitor):
    with pytest.raises(AttributeError):
        monitor.filter_by(None)


def test_filter_by_subsystem_no_dev_type(monitor):
    monitor.filter_by(b'input')
    monitor.filter_by('input')


def test_filter_by_subsystem_no_dev_type_mock(monitor):
    add_match = 'udev_monitor_filter_add_match_subsystem_devtype'
    with pytest.patch_libudev(add_match) as add_match:
        add_match.return_value = 0
        monitor.filter_by(b'input')
        add_match.assert_called_with(monitor._monitor, b'input', None)
        monitor.filter_by('input')
        add_match.assert_called_with(monitor._monitor, b'input', None)
        assert isinstance(add_match.call_args[0][1], bytes)


def test_filter_by_subsystem_dev_type(monitor):
    monitor.filter_by('input', b'usb_interface')
    monitor.filter_by('input', 'usb_interface')


def test_filter_by_subsystem_dev_type_mock(monitor):
    add_match = 'udev_monitor_filter_add_match_subsystem_devtype'
    with pytest.patch_libudev(add_match) as add_match:
        add_match.return_value = 0
        monitor.filter_by(b'input', b'usb_interface')
        add_match.assert_called_with(
            monitor._monitor, b'input', b'usb_interface')
        monitor.filter_by('input', 'usb_interface')
        add_match.assert_called_with(
            monitor._monitor, b'input', b'usb_interface')
        assert isinstance(add_match.call_args[0][2], bytes)


@pytest.check_udev_version('>= 154')
def test_filter_by_tag(monitor):
    monitor.filter_by_tag('spam')


@pytest.check_udev_version('>= 154')
def test_pytest_filter_by_tag_mock(monitor):
    match_tag = 'udev_monitor_filter_add_match_tag'
    with pytest.patch_libudev(match_tag) as match_tag:
        match_tag.return_value = 0
        monitor.filter_by_tag(b'spam')
        match_tag.assert_called_with(monitor._monitor, b'spam')
        monitor.filter_by_tag('eggs')
        match_tag.assert_called_with(monitor._monitor, b'eggs')
        assert isinstance(match_tag.call_args[0][1], bytes)


def test_enable_receiving_netlink_kernel_source(context):
    monitor = Monitor.from_netlink(context, source='kernel')
    monitor.enable_receiving()


def test_enable_receiving_socket(context, socket_path):
    monitor = Monitor.from_socket(context, str(socket_path))
    monitor.enable_receiving()


def test_enable_receiving_bound_socket(context, socket_path):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    # cause an error by binding the socket, thus testing error handling in
    # this method
    sock.bind(str(socket_path))
    monitor = Monitor.from_socket(context, str(socket_path))
    with pytest.raises(EnvironmentError) as exc_info:
        monitor.enable_receiving()
    error = exc_info.value
    assert error.errno == errno.EADDRINUSE
    assert error.strerror == os.strerror(errno.EADDRINUSE)
    assert error.filename == str(socket_path)


def test_enable_receiving_alias():
    assert Monitor.start == Monitor.enable_receiving


def test_enable_receiving_mock(monitor):
    with pytest.patch_libudev('udev_monitor_enable_receiving') as func:
        func.return_value = 0
        monitor.enable_receiving()
        func.assert_called_with(monitor._monitor)


def test_enable_receiving_error_mock(context, monitor, socket_path):
    enable_receiving = 'udev_monitor_enable_receiving'
    get_errno = 'pyudev.monitor.get_libudev_errno'
    with nested(pytest.patch_libudev(enable_receiving),
                mock.patch(get_errno)) as (enable_receiving, get_errno):
            get_errno.return_value = errno.ENOENT
            enable_receiving.return_value = 1
            with pytest.raises(EnvironmentError) as exc_info:
                monitor.enable_receiving()
            error = exc_info.value
            assert error.errno == errno.ENOENT
            assert error.strerror == os.strerror(errno.ENOENT)

            monitor = Monitor.from_socket(context, str(socket_path))
            with pytest.raises(EnvironmentError) as exc_info:
                monitor.enable_receiving()
            error = exc_info.value
            assert error.filename == str(socket_path)


@pytest.mark.privileged
def test_receive_device(monitor):
    # forcibly unload the dummy module to avoid hangs
    pytest.unload_dummy()
    monitor.filter_by('net')
    monitor.enable_receiving()
    # load the dummy device to trigger an add event
    pytest.load_dummy()
    action, device = monitor.receive_device()
    assert action == 'add'
    assert device.subsystem == 'net'
    assert device.device_path == '/devices/virtual/net/dummy0'
    # and unload again
    pytest.unload_dummy()
    action, device = monitor.receive_device()
    assert action == 'remove'
    assert device.subsystem == 'net'
    assert device.device_path == '/devices/virtual/net/dummy0'


def test_receive_device_mock(monitor):
    receive_device = 'udev_monitor_receive_device'
    get_action = 'udev_device_get_action'
    with nested(pytest.patch_libudev(receive_device),
                pytest.patch_libudev(get_action)) as (receive_device,
                                                      get_action):
        receive_device.return_value = mock.sentinel.pointer
        get_action.return_value = b'action'
        action, device = monitor.receive_device()
        assert action == 'action'
        assert pytest.is_unicode_string(action)
        assert isinstance(device, Device)
        assert device.context is monitor.context
        assert device._device is mock.sentinel.pointer
        get_action.assert_called_with(mock.sentinel.pointer)
        receive_device.assert_called_with(monitor._monitor)


def test_receive_device_error_mock(monitor):
    get_errno = 'pyudev.monitor.get_libudev_errno'
    receive_device = 'udev_monitor_receive_device'
    with nested(pytest.patch_libudev(receive_device),
                mock.patch(get_errno)) as (receive_device, get_errno):
        receive_device.return_value = None
        get_errno.return_value = 0
        with pytest.raises(EnvironmentError) as exc_info:
            monitor.receive_device()
        assert str(exc_info.value) == 'Could not receive device'
        get_errno.return_value = errno.ENOENT
        with pytest.raises(EnvironmentError) as exc_info:
            monitor.receive_device()
        error = exc_info.value
        assert error.errno == errno.ENOENT
        assert error.strerror == os.strerror(errno.ENOENT)


@pytest.mark.privileged
def test_iter(monitor):
    pytest.unload_dummy()
    monitor.filter_by('net')
    monitor.enable_receiving()
    pytest.load_dummy()
    iterator = iter(monitor)
    action, device = next(iterator)
    assert action == 'add'
    assert device.subsystem == 'net'
    assert device.device_path == '/devices/virtual/net/dummy0'
    pytest.unload_dummy()
    action, device = next(iterator)
    assert action == 'remove'
    assert device.subsystem == 'net'
    assert device.device_path == '/devices/virtual/net/dummy0'
    iterator.close()
