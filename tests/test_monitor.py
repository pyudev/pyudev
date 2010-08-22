# -*- coding: utf-8 -*-
# Copyright (c) 2010 Sebastian Wiesner <lunaryorn@googlemail.com>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.


import sys
import os
import socket
import errno

import py.test
import mock

import udev
from udev import Monitor, Device

# many tests just consist of some monkey patching to test, that the Monitor
# class actually calls out to udev, correctly passing arguments and handling
# return value.  Actual udev calls are difficult to test, as return values
# and side effects are dynamic and environment-dependent.  It isn't
# necessary anyway, libudev can just assumed to be correct.


def test_from_netlink_invalid_source(context):
    with py.test.raises(ValueError) as exc_info:
        Monitor.from_netlink(context, source='invalid_source')
    message = ('Invalid source: {0!r}. Must be one of "udev" '
               'or "kernel"'.format('invalid_source'))
    assert str(exc_info.value) == message


def _assert_from_netlink_called(context, *args):
    with py.test.patch_libudev('udev_monitor_new_from_netlink') as func:
        source = args[0] if args else 'udev'
        func.return_value = mock.sentinel.pointer
        monitor = Monitor.from_netlink(context, *args)
        func.assert_called_with(context._context, source)
        assert isinstance(func.call_args[0][1], str)
        assert monitor._monitor is mock.sentinel.pointer


def test_from_netlink_source_udev(context):
    monitor = Monitor.from_netlink(context)
    assert monitor._monitor
    monitor = Monitor.from_netlink(context, source=b'udev')
    assert monitor._monitor
    monitor = Monitor.from_netlink(context, source=u'udev')
    assert monitor._monitor


def test_from_netlink_source_udev_mock(context):
    _assert_from_netlink_called(context)
    _assert_from_netlink_called(context, b'udev')
    _assert_from_netlink_called(context, u'udev')


def test_from_netlink_source_kernel(context):
    monitor = Monitor.from_netlink(context, source=b'kernel')
    assert monitor._monitor
    monitor = Monitor.from_netlink(context, source=u'kernel')
    assert monitor._monitor


def test_from_netlink_source_kernel_mock(context):
    _assert_from_netlink_called(context, b'kernel')
    _assert_from_netlink_called(context, 'kernel')


def test_from_socket(context, socket_path):
    monitor = Monitor.from_socket(context, str(socket_path))
    assert monitor._monitor


def test_from_socket_mock(context, socket_path):
    with py.test.patch_libudev('udev_monitor_new_from_socket') as func:
        func.return_value = mock.sentinel.pointer
        monitor = Monitor.from_socket(context, str(socket_path))
        func.assert_called_with(context._context, str(socket_path))
        assert monitor._monitor is mock.sentinel.pointer
        Monitor.from_socket(context, u'foobar')
        func.assert_called_with(context._context, 'foobar')
        assert isinstance(func.call_args[0][1], str)


def test_fileno(monitor):
    # we can't do more than check that no exception is thrown
    monitor.fileno()


def test_fileno_mock(monitor):
    with py.test.patch_libudev('udev_monitor_get_fd') as func:
        func.return_value = mock.sentinel.fileno
        assert monitor.fileno() is mock.sentinel.fileno
        func.assert_called_with(monitor._monitor)


def test_filter_by_no_subsystem(monitor):
    with py.test.raises(AttributeError):
        monitor.filter_by(None)


def test_filter_by_subsystem_no_dev_type(monitor):
    monitor.filter_by(b'input')
    monitor.filter_by(u'input')


def test_filter_by_subsystem_no_dev_type_mock(monitor):
    epic_func_name = 'udev_monitor_filter_add_match_subsystem_devtype'
    with py.test.patch_libudev(epic_func_name) as func:
        func.return_value = 0
        monitor.filter_by(b'input')
        func.assert_called_with(monitor._monitor, b'input', None)
        monitor.filter_by(u'input')
        func.assert_called_with(monitor._monitor, b'input', None)
        assert isinstance(func.call_args[0][1], str)


def test_filter_by_subsystem_dev_type(monitor):
    monitor.filter_by('input', b'usb_interface')
    monitor.filter_by('input', u'usb_interface')


def test_filter_by_subsystem_dev_type_mock(monitor):
    epic_func_name = 'udev_monitor_filter_add_match_subsystem_devtype'
    with py.test.patch_libudev(epic_func_name) as func:
        func.return_value = 0
        monitor.filter_by(b'input', b'usb_interface')
        func.assert_called_with(monitor._monitor, 'input', 'usb_interface')
        monitor.filter_by(u'input', u'usb_interface')
        func.assert_called_with(monitor._monitor, 'input', 'usb_interface')
        assert isinstance(func.call_args[0][2], str)


def test_filter_by_memory_error_mock(monitor):
    epic_func_name = 'udev_monitor_filter_add_match_subsystem_devtype'
    with py.test.patch_libudev(epic_func_name) as func:
        func.return_value = -errno.ENOMEM
        with py.test.raises(MemoryError):
            monitor.filter_by('input')


def test_filter_by_environment_error_mock(monitor):
    epic_func_name = 'udev_monitor_filter_add_match_subsystem_devtype'
    with py.test.patch_libudev(epic_func_name) as func:
        func.return_value = -errno.ENOENT
        with py.test.raises(EnvironmentError) as exc_info:
            monitor.filter_by('input')
        error = exc_info.value
        assert error.errno == errno.ENOENT
        assert error.strerror == os.strerror(errno.ENOENT)


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
    with py.test.raises(EnvironmentError) as exc_info:
        monitor.enable_receiving()
    error = exc_info.value
    assert error.errno == errno.EADDRINUSE
    assert error.strerror == os.strerror(errno.EADDRINUSE)
    assert error.filename == str(socket_path)


def test_enable_receiving_alias():
    assert Monitor.start == Monitor.enable_receiving


def test_enable_receiving_mock(monitor):
    with py.test.patch_libudev('udev_monitor_enable_receiving') as func:
        func.return_value = 0
        monitor.enable_receiving()
        func.assert_called_with(monitor._monitor)


def test_enable_receiving_error_mock(context, monitor, socket_path):
    with py.test.patch_libudev('udev_monitor_enable_receiving') as func:
        with mock.patch('_udev.get_udev_errno') as get_errno:
            get_errno.return_value = errno.ENOENT
            func.return_value = 1
            with py.test.raises(EnvironmentError) as exc_info:
                monitor.enable_receiving()
            error = exc_info.value
            assert error.errno == errno.ENOENT
            assert error.strerror == os.strerror(errno.ENOENT)

            monitor = Monitor.from_socket(context, str(socket_path))
            with py.test.raises(EnvironmentError) as exc_info:
                monitor.enable_receiving()
            error = exc_info.value
            assert error.filename == str(socket_path)


@py.test.mark.skipif("not config.getvalue('allow_privileges')")
@py.test.mark.privileged
def test_receive_device(monitor):
    # forcibly unload the dummy module to avoid hangs
    py.test.unload_dummy()
    monitor.filter_by('net')
    monitor.enable_receiving()
    # load the dummy device to trigger an add event
    py.test.load_dummy()
    action, device = monitor.receive_device()
    assert action == 'add'
    assert device.subsystem == 'net'
    assert device.device_path == '/devices/virtual/net/dummy0'
    # and unload again
    py.test.unload_dummy()
    action, device = monitor.receive_device()
    assert action == 'remove'
    assert device.subsystem == 'net'
    assert device.device_path == '/devices/virtual/net/dummy0'


def test_receive_device_mock(monitor):
    with py.test.patch_libudev('udev_monitor_receive_device') as func:
        with py.test.patch_libudev('udev_device_get_action') as actfunc:
            func.return_value = mock.sentinel.pointer
            actfunc.return_value = b'action'
            action, device = monitor.receive_device()
            assert action == u'action'
            assert isinstance(action, unicode)
            assert isinstance(device, Device)
            assert device.context is monitor.context
            assert device._device is mock.sentinel.pointer
            actfunc.assert_called_with(mock.sentinel.pointer)
            func.assert_called_with(monitor._monitor)


def test_receive_device_error_mock(monitor):
    with py.test.patch_libudev('udev_monitor_receive_device') as func:
        with mock.patch('_udev.get_udev_errno') as errorfunc:
            func.return_value = None
            errorfunc.return_value = 0
            with py.test.raises(EnvironmentError) as exc_info:
                monitor.receive_device()
            assert str(exc_info.value) == 'Could not receive device'
            errorfunc.return_value = errno.ENOENT
            with py.test.raises(EnvironmentError) as exc_info:
                monitor.receive_device()
            error = exc_info.value
            assert error.errno == errno.ENOENT
            assert error.strerror == os.strerror(errno.ENOENT)


@py.test.mark.skipif("not config.getvalue('allow_privileges')")
@py.test.mark.privileged
def test_iter(monitor):
    py.test.unload_dummy()
    monitor.filter_by('net')
    monitor.enable_receiving()
    py.test.load_dummy()
    iterator = iter(monitor)
    action, device = next(iterator)
    assert action == 'add'
    assert device.subsystem == 'net'
    assert device.device_path == '/devices/virtual/net/dummy0'
    py.test.unload_dummy()
    action, device = next(iterator)
    assert action == 'remove'
    assert device.subsystem == 'net'
    assert device.device_path == '/devices/virtual/net/dummy0'
    iterator.close()
