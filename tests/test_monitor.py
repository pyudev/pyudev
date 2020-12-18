# -*- coding: utf-8 -*-
# Copyright (C) 2010, 2011, 2012, 2013 Sebastian Wiesner <lunaryorn@gmail.com>

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
import random
from contextlib import contextmanager
from datetime import datetime, timedelta
from select import select

# isort: THIRDPARTY
import pytest
from tests._constants import _UDEV_TEST
from tests.utils.udev import DeviceDatabase

# isort: LOCAL
from pyudev import Devices, Monitor, MonitorObserver

try:
    from unittest import mock
except ImportError:
    import mock


# many tests just consist of some monkey patching to test, that the Monitor
# class actually calls out to udev, correctly passing arguments and handling
# return value.  Actual udev calls are difficult to test, as return values
# and side effects are dynamic and environment-dependent.  It isn't
# necessary anyway, libudev can just assumed to be correct.


@pytest.fixture
def monitor(request):
    return Monitor.from_netlink(request.getfixturevalue("context"))


@pytest.fixture
def fake_monitor_device(request):
    context = request.getfixturevalue("context")
    device = random.choice(list(DeviceDatabase.db()))
    return Devices.from_path(context, device.device_path)


@contextmanager
def patch_filter_by(type):
    add_match = "udev_monitor_filter_add_match_{0}".format(type)
    filter_update = "udev_monitor_filter_update"
    with pytest.patch_libudev(add_match) as add_match:
        add_match.return_value = 0
        with pytest.patch_libudev(filter_update) as filter_update:
            filter_update.return_value = 0
            yield add_match, filter_update


class TestMonitor(object):
    def test_from_netlink_invalid_source(self, context):
        with pytest.raises(ValueError) as exc_info:
            Monitor.from_netlink(context, source="invalid_source")
        message = 'Invalid source: {0!r}. Must be one of "udev" ' 'or "kernel"'.format(
            "invalid_source"
        )
        assert str(exc_info.value) == message

    def test_from_netlink_source_udev(self, context):
        monitor = Monitor.from_netlink(context)
        assert monitor._as_parameter_
        assert not monitor.started
        monitor = Monitor.from_netlink(context, source="udev")
        assert monitor._as_parameter_
        assert not monitor.started

    def test_from_netlink_source_udev_mock(self, context):
        funcname = "udev_monitor_new_from_netlink"
        spec = lambda c, s: None
        with mock.patch.object(context._libudev, funcname, autospec=spec) as func:
            func.return_value = mock.sentinel.monitor
            monitor = Monitor.from_netlink(context)
            assert monitor._as_parameter_ is mock.sentinel.monitor
            assert not monitor.started
            func.assert_called_once_with(context, b"udev")
            func.reset_mock()
            monitor = Monitor.from_netlink(context, "udev")
            assert monitor._as_parameter_ is mock.sentinel.monitor
            assert not monitor.started
            func.assert_called_once_with(context, b"udev")

    def test_from_netlink_source_kernel(self, context):
        monitor = Monitor.from_netlink(context, source="kernel")
        assert monitor._as_parameter_
        assert not monitor.started

    def test_from_netlink_source_kernel_mock(self, context):
        funcname = "udev_monitor_new_from_netlink"
        spec = lambda c, s: None
        with mock.patch.object(context._libudev, funcname, autospec=spec) as func:
            func.return_value = mock.sentinel.monitor
            monitor = Monitor.from_netlink(context, "kernel")
            assert monitor._as_parameter_ is mock.sentinel.monitor
            assert not monitor.started
            func.assert_called_once_with(context, b"kernel")

    def test_fileno(self, monitor):
        # we can't do more than check that no exception is thrown
        monitor.fileno()

    def test_fileno_mock(self, monitor):
        funcname = "udev_monitor_get_fd"
        spec = lambda m: None
        with mock.patch.object(monitor._libudev, funcname, autospec=spec) as func:
            func.return_value = mock.sentinel.fileno
            assert monitor.fileno() is mock.sentinel.fileno
            func.assert_called_once_with(monitor)

    def test_filter_by_no_subsystem(self, monitor):
        with pytest.raises(AttributeError):
            monitor.filter_by(None)

    def test_filter_by_subsystem_no_dev_type(self, monitor):
        monitor.filter_by(b"input")
        monitor.filter_by("input")

    def test_filter_by_subsystem_no_dev_type_mock(self, monitor):
        funcname = "udev_monitor_filter_add_match_subsystem_devtype"
        spec = lambda m, s, t: None
        libudev = monitor._libudev
        with mock.patch.object(libudev, funcname, autospec=spec) as match:
            funcname = "udev_monitor_filter_update"
            spec = lambda m: None
            with mock.patch.object(libudev, funcname, autospec=spec) as update:
                monitor.filter_by("input")
                match.assert_called_once_with(monitor, b"input", None)
                update.assert_called_once_with(monitor)

    def test_filter_by_subsystem_dev_type(self, monitor):
        monitor.filter_by("input", b"usb_interface")
        monitor.filter_by("input", "usb_interface")

    def test_filter_by_subsystem_dev_type_mock(self, monitor):
        funcname = "udev_monitor_filter_add_match_subsystem_devtype"
        spec = lambda m, s, t: None
        libudev = monitor._libudev
        with mock.patch.object(libudev, funcname, autospec=spec) as match:
            funcname = "udev_monitor_filter_update"
            spec = lambda m: None
            with mock.patch.object(libudev, funcname, autospec=spec) as update:
                monitor.filter_by("input", "usb_interface")
                match.assert_called_once_with(monitor, b"input", b"usb_interface")
                update.assert_called_once_with(monitor)

    @_UDEV_TEST(154, "test_filter_by_tag")
    def test_filter_by_tag(self, monitor):
        monitor.filter_by_tag("spam")

    @_UDEV_TEST(154, "test_filter_by_tag")
    def test_filter_by_tag_mock(self, monitor):
        funcname = "udev_monitor_filter_add_match_tag"
        spec = lambda m, t: None
        libudev = monitor._libudev
        with mock.patch.object(libudev, funcname, autospec=spec) as match:
            funcname = "udev_monitor_filter_update"
            spec = lambda m: None
            with mock.patch.object(libudev, funcname, autospec=spec) as update:
                monitor.filter_by_tag("eggs")
                match.assert_called_once_with(monitor, b"eggs")
                update.assert_called_once_with(monitor)

    def test_remove_filter(self, monitor):
        """
        The underlying ``udev_monitor_filter_remove()`` is apparently broken.
        It always causes ``EINVAL`` from ``setsockopt()``. In some version
        it changed and it now raises FileNotFoundError.
        """
        with pytest.raises(Exception):
            monitor.remove_filter()

    def test_remove_filter_mock(self, monitor):
        funcname = "udev_monitor_filter_remove"
        libudev = monitor._libudev
        spec = lambda m: None
        with mock.patch.object(libudev, funcname, autospec=spec) as remove:
            funcname = "udev_monitor_filter_update"
            with mock.patch.object(libudev, funcname, autospec=spec) as update:
                monitor.remove_filter()
                remove.assert_called_once_with(monitor)
                update.assert_called_once_with(monitor)

    def test_start_netlink_kernel_source(self, context):
        monitor = Monitor.from_netlink(context, source="kernel")
        assert not monitor.started
        monitor.start()
        assert monitor.started

    def test_start_mock(self, monitor):
        funcname = "udev_monitor_enable_receiving"
        spec = lambda m: None
        with mock.patch.object(monitor._libudev, funcname, autospec=spec) as func:
            assert not monitor.started
            monitor.start()
            assert monitor.started
            monitor.start()
            func.assert_called_once_with(monitor)

    def test_enable_receiving(self, monitor):
        """
        Test that enable_receiving() is deprecated and calls out to start().
        """
        with mock.patch.object(monitor, "start") as start:
            pytest.deprecated_call(monitor.enable_receiving)
            assert start.called

    def test_set_receive_buffer_size_mock(self, monitor):
        funcname = "udev_monitor_set_receive_buffer_size"
        spec = lambda m, s: None
        with mock.patch.object(monitor._libudev, funcname, autospec=spec) as func:
            monitor.set_receive_buffer_size(1000)
            func.assert_called_once_with(monitor, 1000)

    def test_poll_timeout(self, monitor):
        assert monitor.poll(timeout=0) is None
        now = datetime.now()
        assert monitor.poll(timeout=1) is None
        assert datetime.now() - now >= timedelta(seconds=1)

    def test_receive_device(self, monitor):
        """
        Test that Monitor.receive_device is deprecated and calls out to
        poll(), which in turn is tested by test_poll.
        """
        with mock.patch.object(monitor, "poll") as poll:
            device = mock.Mock(name="device")
            device.action = "spam"
            poll.return_value = device
            event = pytest.deprecated_call(monitor.receive_device)
            assert event[0] == "spam"
            assert event[1] is device


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
            if pytest.__version__ == "2.8.4":
                self.observer = MonitorObserver(
                    monitor, event_handler=self.event_handler
                )
            else:
                self.observer = pytest.deprecated_call(
                    MonitorObserver, monitor, event_handler=self.event_handler
                )
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
        assert not observer.is_alive()
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
        assert not observer.is_alive()
        # check that we got two events
        assert self.events == [fake_monitor_device] * 2
