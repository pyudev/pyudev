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

import errno
from datetime import datetime, timedelta
from contextlib import contextmanager
from select import select

import pytest
from mock import Mock, sentinel, patch

from pyudev import Monitor, MonitorObserver, Device
from pyudev._libudev import libudev

# many tests just consist of some monkey patching to test, that the Monitor
# class actually calls out to udev, correctly passing arguments and handling
# return value.  Actual udev calls are difficult to test, as return values
# and side effects are dynamic and environment-dependent.  It isn't
# necessary anyway, libudev can just assumed to be correct.


def pytest_funcarg__monitor(request):
    return Monitor.from_netlink(request.getfuncargvalue('context'))


def pytest_funcarg__fake_monitor_device(request):
    context = request.getfuncargvalue('context')
    return Device.from_path(context, '/devices/platform')


@contextmanager
def patch_filter_by(type):
    add_match = 'udev_monitor_filter_add_match_{0}'.format(type)
    filter_update = 'udev_monitor_filter_update'
    with pytest.patch_libudev(add_match) as add_match:
        add_match.return_value = 0
        with pytest.patch_libudev(filter_update) as filter_update:
            filter_update.return_value = 0
            yield add_match, filter_update


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
        assert not monitor.started
        monitor = Monitor.from_netlink(context, source='udev')
        assert monitor._as_parameter_
        assert not monitor.started

    def test_from_netlink_source_udev_mock(self, context):
        calls = {'udev_monitor_new_from_netlink':
                 [(context, b'udev'), (context, b'udev')]}
        with pytest.calls_to_libudev(calls):
            libudev.udev_monitor_new_from_netlink.return_value = sentinel.monitor
            monitor = Monitor.from_netlink(context)
            assert monitor._as_parameter_ is sentinel.monitor
            assert not monitor.started
            monitor = Monitor.from_netlink(context, 'udev')
            assert monitor._as_parameter_ is sentinel.monitor
            assert not monitor.started

    def test_from_netlink_source_kernel(self, context):
        monitor = Monitor.from_netlink(context, source='kernel')
        assert monitor._as_parameter_
        assert not monitor.started

    def test_from_netlink_source_kernel_mock(self, context):
        calls = {'udev_monitor_new_from_netlink': [(context, b'kernel')]}
        with pytest.calls_to_libudev(calls):
            libudev.udev_monitor_new_from_netlink.return_value = sentinel.monitor
            monitor = Monitor.from_netlink(context, 'kernel')
            assert monitor._as_parameter_ is sentinel.monitor
            assert not monitor.started

    def test_fileno(self, monitor):
        # we can't do more than check that no exception is thrown
        monitor.fileno()

    def test_fileno_mock(self, monitor):
        calls = {'udev_monitor_get_fd': [(monitor,)]}
        with pytest.calls_to_libudev(calls):
            libudev.udev_monitor_get_fd.return_value = sentinel.fileno
            assert monitor.fileno() is sentinel.fileno

    def test_filter_by_no_subsystem(self, monitor):
        with pytest.raises(AttributeError):
            monitor.filter_by(None)

    def test_filter_by_subsystem_no_dev_type(self, monitor):
        monitor.filter_by(b'input')
        monitor.filter_by('input')

    def test_filter_by_subsystem_no_dev_type_mock(self, monitor):
        calls = {'udev_monitor_filter_add_match_subsystem_devtype':
                 [(monitor, b'input', None)],
                 'udev_monitor_filter_update': [(monitor,)]}
        with pytest.calls_to_libudev(calls):
            monitor.filter_by('input')

    def test_filter_by_subsystem_dev_type(self, monitor):
        monitor.filter_by('input', b'usb_interface')
        monitor.filter_by('input', 'usb_interface')

    def test_filter_by_subsystem_dev_type_mock(self, monitor):
        calls = {'udev_monitor_filter_add_match_subsystem_devtype':
                 [(monitor, b'input', b'usb_interface')],
                 'udev_monitor_filter_update': [(monitor,)]}
        with pytest.calls_to_libudev(calls):
            monitor.filter_by('input', 'usb_interface')

    @pytest.mark.udev_version('>= 154')
    def test_filter_by_tag(self, monitor):
        monitor.filter_by_tag('spam')

    @pytest.mark.udev_version('>= 154')
    def test_filter_by_tag_mock(self, monitor):
        calls = {'udev_monitor_filter_add_match_tag': [(monitor, b'eggs')],
                 'udev_monitor_filter_update': [(monitor,)]}
        with pytest.calls_to_libudev(calls):
            monitor.filter_by_tag('eggs')

    def test_remove_filter(self, monitor):
        """
        The underlying ``udev_monitor_filter_remove()`` is apparently broken.
        It always causes ``EINVAL`` from ``setsockopt()``.
        """
        with pytest.raises(ValueError):
            monitor.remove_filter()

    def test_remove_filter_mock(self, monitor):
        calls = {'udev_monitor_filter_remove': [(monitor,)],
                 'udev_monitor_filter_update': [(monitor,)]}
        with pytest.calls_to_libudev(calls):
            monitor.remove_filter()

    def test_start_netlink_kernel_source(self, context):
        monitor = Monitor.from_netlink(context, source='kernel')
        assert not monitor.started
        monitor.start()
        assert monitor.started

    def test_start_mock(self, monitor):
        calls = {'udev_monitor_enable_receiving': [(monitor,)]}
        with pytest.calls_to_libudev(calls):
            assert not monitor.started
            monitor.start()
            assert monitor.started

    def test_enable_receiving(self, monitor):
        """
        Test that enable_receiving() is deprecated and calls out to start().
        """
        with patch.object(monitor, 'start') as start:
            pytest.deprecated_call(monitor.enable_receiving)
            assert start.called

    def test_set_receive_buffer_size_mock(self, monitor):
        calls = {'udev_monitor_set_receive_buffer_size': [(monitor, 1000)]}
        with pytest.calls_to_libudev(calls):
            monitor.set_receive_buffer_size(1000)

    def test_set_receive_buffer_size_privilege_error(self, monitor):
        with pytest.raises(EnvironmentError) as exc_info:
            monitor.set_receive_buffer_size(1000)
        pytest.assert_env_error(exc_info.value, errno.EPERM)

    def test_poll_timeout(self, monitor):
        assert monitor.poll(timeout=0) is None
        now = datetime.now()
        assert monitor.poll(timeout=1) is None
        assert datetime.now() - now >= timedelta(seconds=1)

    @pytest.mark.privileged
    def test_poll(self, monitor):
        # forcibly unload the dummy module to avoid hangs
        pytest.unload_dummy()
        monitor.filter_by('net')
        monitor.start()
        # load the dummy device to trigger an add event
        pytest.load_dummy()
        select([monitor], [], [])
        device = monitor.poll()
        assert device.action == 'add'
        assert device.sequence_number > 0
        assert device.subsystem == 'net'
        assert device.device_path == '/devices/virtual/net/dummy0'
        # and unload again
        pytest.unload_dummy()
        device = monitor.poll()
        assert device.action == 'remove'
        assert device.sequence_number > 0
        assert device.subsystem == 'net'
        assert device.device_path == '/devices/virtual/net/dummy0'

    def test_receive_device(self, monitor):
        """
        Test that Monitor.receive_device is deprecated and calls out to
        _receive_device(), which in turn is tested by test_poll.
        """
        with patch.object(monitor, '_receive_device') as receive_device:
            device = Mock(name='device')
            device.action = 'spam'
            receive_device.return_value = device
            event = pytest.deprecated_call(monitor.receive_device)
            assert event[0] == 'spam'
            assert event[1] is device

    @pytest.mark.privileged
    def test_iter(self, monitor):
        pytest.unload_dummy()
        monitor.filter_by('net')
        monitor.start()
        pytest.load_dummy()
        iterator = iter(monitor)
        # DeprecationWarning triggered on first invocation of generator
        action, device = pytest.deprecated_call(next, iterator)
        assert action == 'add'
        assert device.action == 'add'
        assert device.sequence_number > 0
        assert device.subsystem == 'net'
        assert device.device_path == '/devices/virtual/net/dummy0'
        pytest.unload_dummy()
        action, device = next(iterator)
        assert action == 'remove'
        assert device.action == 'remove'
        assert device.sequence_number > 0
        assert device.subsystem == 'net'
        assert device.device_path == '/devices/virtual/net/dummy0'
        iterator.close()


class TestMonitorObserver(object):

    def callback(self, device):
        self.events.append(device)
        if len(self.events) >= 2:
            self.observer.send_stop()

    def event_handler(self, action, device):
        self.events.append((action, device))
        if len(self.events) >= 2:
            self.observer.send_stop()

    def make_observer(self, monitor, use_deprecated=False):
        if use_deprecated:
            self.observer = pytest.deprecated_call(
                MonitorObserver, monitor, event_handler=self.event_handler)
        else:
            self.observer = MonitorObserver(monitor, callback=self.callback)
        return self.observer

    def setup(self):
        self.events = []

    def teardown(self):
        self.events = None

    def test_deprecated_handler(self, fake_monitor, fake_monitor_device):
        observer = self.make_observer(fake_monitor, use_deprecated=True)
        observer.start()
        fake_monitor.trigger_event()
        fake_monitor.trigger_event()
        # wait a second for the tests to finish, and kill the observer if
        # it is still alive then
        observer.join(1)
        if observer.is_alive():
            observer.stop()
        assert self.events == [(None, fake_monitor_device)] * 2

    def test_fake(self, fake_monitor, fake_monitor_device):
        observer = self.make_observer(fake_monitor)
        observer.start()
        fake_monitor.trigger_event()
        fake_monitor.trigger_event()
        # wait a second for the tests to finish
        observer.join(1)
        # forcibly quit the thread if it is still alive
        if observer.is_alive():
            observer.stop()
        # check that we got two events
        assert self.events == [fake_monitor_device] * 2

    @pytest.mark.privileged
    def test_real(self, context, monitor):
        observer = self.make_observer(monitor)
        pytest.unload_dummy()
        monitor.filter_by('net')
        monitor.start()
        observer.start()
        pytest.load_dummy()
        pytest.unload_dummy()
        observer.join(2)
        if observer.is_alive():
            observer.stop()
        assert [d.action for d in self.events] == ['add', 'remove']
        for device in self.events:
            assert device.device_path == '/devices/virtual/net/dummy0'
