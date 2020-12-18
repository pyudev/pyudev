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

# isort: THIRDPARTY
import pytest
from tests.utils.udev import DeviceDatabase

# isort: LOCAL
from pyudev import Devices, Monitor

try:
    from unittest import mock
except ImportError:
    import mock


@pytest.fixture
def monitor(request):
    return Monitor.from_netlink(request.getfixturevalue("context"))


@pytest.fixture
def fake_monitor_device(request):
    context = request.getfixturevalue("context")
    device = random.choice(list(DeviceDatabase.db()))
    return Devices.from_path(context, device.device_path)


def test_fake_monitor(fake_monitor, fake_monitor_device):
    """
    Test the fake monitor just to make sure, that it works.
    """
    assert fake_monitor.poll(timeout=0) is None
    fake_monitor.trigger_event()
    device = fake_monitor.poll()
    assert device == fake_monitor_device


class ObserverTestBase(object):
    def setup_method(self, method):
        self.observer = None
        self.no_emitted_signals = 0
        self.setup()

    def teardown_method(self, method):
        if self.observer is not None:
            self.destroy_observer()
        self.teardown()

    def setup(self):
        pass

    def teardown(self):
        pass

    def destroy_observer(self):
        self.observer.enabled = False

    def create_observer(self, monitor):
        raise NotImplementedError()

    def create_event_loop(self, self_stop_timeout=5000):
        raise NotImplementedError()

    def start_event_loop(self, start_callback):
        raise NotImplementedError()

    def stop_event_loop(self):
        raise NotImplementedError()

    def connect_signal(self, callback, action=None):
        raise NotImplementedError()

    def prepare_test(self, monitor):
        self.create_event_loop(self_stop_timeout=5000)
        self.create_observer(monitor)

    def test_monitor(self, fake_monitor):
        self.prepare_test(fake_monitor)
        # test that the monitor attribute is correct
        assert self.observer.monitor is fake_monitor

    def test_events_fake_monitor(self, fake_monitor, fake_monitor_device):
        self.prepare_test(fake_monitor)
        event_callback = mock.Mock(side_effect=lambda *args: self.stop_event_loop())
        self.connect_signal(event_callback)

        self.start_event_loop(fake_monitor.trigger_event)
        event_callback.assert_called_with(fake_monitor_device)


class QtObserverTestBase(ObserverTestBase):
    def setup(self):
        self.qtcore = pytest.importorskip("{0}.QtCore".format(self.BINDING_NAME))

    def create_observer(self, monitor):
        name = self.BINDING_NAME.lower()
        mod = __import__("pyudev.{0}".format(name), None, None, [name])
        self.observer = mod.MonitorObserver(monitor)

    def connect_signal(self, callback):
        self.observer.deviceEvent.connect(callback)

    def create_event_loop(self, self_stop_timeout=5000):
        self.app = self.qtcore.QCoreApplication.instance()
        if not self.app:
            self.app = self.qtcore.QCoreApplication([])
        self.qtcore.QTimer.singleShot(self_stop_timeout, self.stop_event_loop)

    def start_event_loop(self, start_callback):
        self.qtcore.QTimer.singleShot(0, start_callback)
        self.app.exec_()

    def stop_event_loop(self):
        self.app.quit()


class TestPysideObserver(QtObserverTestBase):
    BINDING_NAME = "PySide"


class TestPyQt4Observer(QtObserverTestBase):
    BINDING_NAME = "PyQt4"


class TestPyQt5Observer(QtObserverTestBase):
    BINDING_NAME = "PyQt5"


class TestGlibObserver(ObserverTestBase):
    def setup(self):
        self.event_sources = []
        pytest.importorskip("gi")
        self.glib = pytest.importorskip("gi.repository.GLib")

    def teardown(self):
        for source in self.event_sources:
            self.glib.source_remove(source)

    def create_observer(self, monitor):
        from pyudev.glib import MonitorObserver

        self.observer = MonitorObserver(monitor)

    def connect_signal(self, callback):
        # drop the sender argument from glib signal connections
        def _wrapper(obj, *args, **kwargs):
            return callback(*args, **kwargs)

        self.observer.connect("device-event", _wrapper)

    def create_event_loop(self, self_stop_timeout=5000):
        self.mainloop = self.glib.MainLoop()
        self.event_sources.append(
            self.glib.timeout_add(self_stop_timeout, self.stop_event_loop)
        )

    def start_event_loop(self, start_callback):
        def _wrapper(*args, **kwargs):
            start_callback(*args, **kwargs)
            return False

        self.event_sources.append(self.glib.timeout_add(0, _wrapper))
        self.mainloop.run()

    def stop_event_loop(self):
        self.mainloop.quit()
        return False


@pytest.mark.skipif(
    str('"DISPLAY" not in os.environ'), reason="Display required for wxPython"
)
class TestWxObserver(ObserverTestBase):
    def setup(self):
        self.wx = pytest.importorskip("wx")

    def create_observer(self, monitor):
        from pyudev import wx

        self.observer = wx.MonitorObserver(monitor)

    def connect_signal(self, callback):
        from pyudev.wx import EVT_DEVICE_EVENT

        def _wrapper(event):
            return callback(event.device)

        self.observer.Bind(EVT_DEVICE_EVENT, _wrapper)

    def create_event_loop(self, self_stop_timeout=5000):
        self.app = self.wx.App(False)
        # need to create a dummy Frame to get the mainloop running. Praise the
        # broken wx API…
        self.app.frame = self.wx.Frame(None)
        timer = self.wx.PyTimer(self.stop_event_loop)
        timer.Start(self_stop_timeout, True)

    def start_event_loop(self, start_callback):
        timer = self.wx.PyTimer(start_callback)
        timer.Start(0, True)
        self.app.MainLoop()

    def stop_event_loop(self):
        self.app.Exit()
