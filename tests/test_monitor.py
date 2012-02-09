# -*- coding: utf-8 -*-
# Copyright (C) 2010, 2011, 2012 Sebastian Wiesner <lunaryorn@googlemail.com>

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
import socket
import errno
from select import select
from operator import itemgetter

import pytest
import mock

from pyudev import Monitor, MonitorObserver, Device

# many tests just consist of some monkey patching to test, that the Monitor
# class actually calls out to udev, correctly passing arguments and handling
# return value.  Actual udev calls are difficult to test, as return values
# and side effects are dynamic and environment-dependent.  It isn't
# necessary anyway, libudev can just assumed to be correct.


def _assert_from_netlink_called(context, *args):
    new_from_netlink = 'udev_monitor_new_from_netlink'
    with pytest.patch_libudev(new_from_netlink) as new_from_netlink:
        source = args[0].encode('ascii') if args else b'udev'
        new_from_netlink.return_value = mock.sentinel.pointer
        monitor = Monitor.from_netlink(context, *args)
        new_from_netlink.assert_called_with(context, source)
        assert isinstance(new_from_netlink.call_args[0][1], bytes)
        assert monitor._as_parameter_ is mock.sentinel.pointer


class TestMonitor(object):

    def test_from_netlink_invalid_source(self, context):
        with pytest.raises(ValueError) as exc_info:
            Monitor.from_netlink(context, source='invalid_source')
        message = ('Invalid source: {0!r}. Must be one of "udev" '
                   'or "kernel"'.format('invalid_source'))
        assert str(exc_info.value) == message

    def test_from_netlink_source_udev(self, context):
        monitor = Monitor.from_netlink(context)
        assert monitor._as_parameter_
        monitor = Monitor.from_netlink(context, source='udev')
        assert monitor._as_parameter_

    def test_from_netlink_source_udev_mock(self, context):
        _assert_from_netlink_called(context)
        _assert_from_netlink_called(context, 'udev')

    def test_from_netlink_source_kernel(self, context):
        monitor = Monitor.from_netlink(context, source='kernel')
        assert monitor._as_parameter_

    def test_from_netlink_source_kernel_mock(self, context):
        _assert_from_netlink_called(context, 'kernel')

    def test_from_socket(self, context, socket_path):
        monitor = Monitor.from_socket(context, str(socket_path))
        assert monitor._as_parameter_

    def test_from_socket_mock(self, context, socket_path):
        socket_path = str(socket_path)
        new_from_socket = 'udev_monitor_new_from_socket'
        with pytest.patch_libudev(new_from_socket) as new_from_socket:
            new_from_socket.return_value = mock.sentinel.pointer
            monitor = Monitor.from_socket(context, socket_path)
            new_from_socket.assert_called_with(
                context, socket_path.encode(sys.getfilesystemencoding()))
            assert monitor._as_parameter_ is mock.sentinel.pointer
            Monitor.from_socket(context, 'foobar')
            new_from_socket.assert_called_with(context, b'foobar')
            assert isinstance(new_from_socket.call_args[0][1], bytes)

    def test_fileno(self, monitor):
        # we can't do more than check that no exception is thrown
        monitor.fileno()

    def test_fileno_mock(self, monitor):
        get_fd = 'udev_monitor_get_fd'
        with pytest.patch_libudev(get_fd) as get_fd:
            get_fd.return_value = mock.sentinel.fileno
            assert monitor.fileno() is mock.sentinel.fileno
            get_fd.assert_called_with(monitor)

    def test_filter_by_no_subsystem(self, monitor):
        with pytest.raises(AttributeError):
            monitor.filter_by(None)

    def test_filter_by_subsystem_no_dev_type(self, monitor):
        monitor.filter_by(b'input')
        monitor.filter_by('input')

    def test_filter_by_subsystem_no_dev_type_mock(self, monitor):
        add_match = 'udev_monitor_filter_add_match_subsystem_devtype'
        with pytest.patch_libudev(add_match) as add_match:
            add_match.return_value = 0
            monitor.filter_by(b'input')
            add_match.assert_called_with(monitor, b'input', None)
            monitor.filter_by('input')
            add_match.assert_called_with(monitor, b'input', None)
            assert isinstance(add_match.call_args[0][1], bytes)

    def test_filter_by_subsystem_dev_type(self, monitor):
        monitor.filter_by('input', b'usb_interface')
        monitor.filter_by('input', 'usb_interface')

    def test_filter_by_subsystem_dev_type_mock(self, monitor):
        add_match = 'udev_monitor_filter_add_match_subsystem_devtype'
        with pytest.patch_libudev(add_match) as add_match:
            add_match.return_value = 0
            monitor.filter_by(b'input', b'usb_interface')
            add_match.assert_called_with(monitor, b'input', b'usb_interface')
            monitor.filter_by('input', 'usb_interface')
            add_match.assert_called_with(monitor, b'input', b'usb_interface')
            assert isinstance(add_match.call_args[0][2], bytes)

    @pytest.need_udev_version('>= 154')
    def test_filter_by_tag(self, monitor):
        monitor.filter_by_tag('spam')

    @pytest.need_udev_version('>= 154')
    def test_pytest_filter_by_tag_mock(self, monitor):
        match_tag = 'udev_monitor_filter_add_match_tag'
        with pytest.patch_libudev(match_tag) as match_tag:
            match_tag.return_value = 0
            monitor.filter_by_tag(b'spam')
            match_tag.assert_called_with(monitor, b'spam')
            monitor.filter_by_tag('eggs')
            match_tag.assert_called_with(monitor, b'eggs')
            assert isinstance(match_tag.call_args[0][1], bytes)

    def test_enable_receiving_netlink_kernel_source(self, context):
        monitor = Monitor.from_netlink(context, source='kernel')
        monitor.enable_receiving()

    def test_enable_receiving_socket(self, context, socket_path):
        monitor = Monitor.from_socket(context, str(socket_path))
        monitor.enable_receiving()

    def test_enable_receiving_bound_socket(self, context, socket_path):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        # cause an error by binding the socket, thus testing error handling in
        # this method
        sock.bind(str(socket_path))
        monitor = Monitor.from_socket(context, str(socket_path))
        with pytest.raises(EnvironmentError) as exc_info:
            monitor.enable_receiving()
        pytest.assert_env_error(exc_info.value, errno.EADDRINUSE, str(socket_path))

    def test_enable_receiving_alias(self):
        assert Monitor.start == Monitor.enable_receiving

    def test_enable_receiving_mock(self, monitor):
        with pytest.patch_libudev('udev_monitor_enable_receiving') as func:
            func.return_value = 0
            monitor.enable_receiving()
            func.assert_called_with(monitor)

    def test_set_receive_buffer_size_mock(self, monitor):
        set_receive_buffer_size = 'udev_monitor_set_receive_buffer_size'
        with pytest.patch_libudev(set_receive_buffer_size) as func:
            func.return_value = 0
            monitor.set_receive_buffer_size(1000)
            func.assert_called_with(monitor, 1000)

    def test_set_receive_buffer_size_privilege_error(self, monitor,
                                                     socket_path):
        with pytest.raises(EnvironmentError) as exc_info:
            monitor.set_receive_buffer_size(1000)
        pytest.assert_env_error(exc_info.value, errno.EPERM)

    @pytest.mark.privileged
    def test_receive_device(self, monitor):
        # forcibly unload the dummy module to avoid hangs
        pytest.unload_dummy()
        monitor.filter_by('net')
        monitor.enable_receiving()
        # load the dummy device to trigger an add event
        pytest.load_dummy()
        select([monitor], [], [])
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

    def test_receive_device_mock(self, monitor):
        receive_device = 'udev_monitor_receive_device'
        get_action = 'udev_device_get_action'
        with pytest.nested(pytest.patch_libudev(receive_device),
                           pytest.patch_libudev(get_action)) as (receive_device,
                                                                 get_action):
            receive_device.return_value = mock.sentinel.pointer
            get_action.return_value = b'action'
            action, device = monitor.receive_device()
            assert action == 'action'
            assert pytest.is_unicode_string(action)
            assert isinstance(device, Device)
            assert device.context is monitor.context
            assert device._as_parameter_ is mock.sentinel.pointer
            get_action.assert_called_with(mock.sentinel.pointer)
            receive_device.assert_called_with(monitor)

    @pytest.mark.privileged
    def test_iter(self, monitor):
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


class TestMonitorObserver(object):

    def receive_event(self, action, device):
        self.events.append((action, device))
        if len(self.events) >= 2:
            self.observer.send_stop()

    def make_observer(self, monitor):
        self.observer = MonitorObserver(monitor, self.receive_event)
        return self.observer

    def setup(self):
        self.events = []

    def teardown(self):
        self.events = None

    def test_fake(self, fake_monitor, platform_device):
        observer = self.make_observer(fake_monitor)
        observer.start()
        fake_monitor.trigger_action('add')
        fake_monitor.trigger_action('remove')
        # fake one second for the tests to finish
        observer.join(1)
        # forcibly quit the thread if it is still alive
        if observer.is_alive():
            observer.stop()
        # check that we got two events
        assert self.events == [('add', platform_device), ('remove', platform_device)]

    @pytest.mark.privileged
    def test_real(self, context, monitor):
        observer = self.make_observer(monitor)
        pytest.unload_dummy()
        monitor.filter_by('net')
        monitor.enable_receiving()
        observer.start()
        pytest.load_dummy()
        pytest.unload_dummy()
        observer.join(2)
        if observer.is_alive():
            observer.stop()
        assert map(itemgetter(0), self.events) == ['add', 'remove']
        assert all(device.device_path == '/devices/virtual/net/dummy0' for _, device in self.events)

