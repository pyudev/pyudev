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

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import pytest
import mock

from pyudev import Monitor, Devices


@pytest.fixture
def monitor(request):
    return Monitor.from_netlink(request.getfuncargvalue('context'))


@pytest.fixture
def fake_monitor_device(request):
    context = request.getfuncargvalue('context')
    return Devices.from_path(context, '/devices/platform')


ACTIONS = ('add', 'remove', 'change', 'move')


class DeprecatedObserverTestBase(object):

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

    def stop_when_done(self, *args, **kwargs):
        self.no_emitted_signals += 1
        if self.no_emitted_signals >= 2:
            self.stop_event_loop()

    def prepare_test(self, monitor):
        self.create_event_loop(self_stop_timeout=5000)
        self.create_observer(monitor)

    def test_monitor(self, fake_monitor):
        self.prepare_test(fake_monitor)
        # test that the monitor attribute is correct
        assert self.observer.monitor is fake_monitor

    @pytest.mark.parametrize('action', ACTIONS, ids=ACTIONS)
    def test_events_fake_monitor(self, action, fake_monitor,
                                 fake_monitor_device):
        self.prepare_test(fake_monitor)
        event_callback = mock.Mock(side_effect=self.stop_when_done)
        action_callback = mock.Mock(side_effect=self.stop_when_done)
        self.connect_signal(event_callback)
        self.connect_signal(action_callback, action=action)
        funcname = 'udev_device_get_action'
        spec = lambda d: None
        with mock.patch.object(fake_monitor_device._libudev, funcname,
                               autospec=spec) as func:
            func.return_value = action.encode('ascii')
            self.start_event_loop(fake_monitor.trigger_event)
            func.assert_called_with(fake_monitor_device)
        event_callback.assert_called_with(action, fake_monitor_device)
        action_callback.assert_called_with(fake_monitor_device)

    @pytest.mark.privileged
    def test_events_real(self, context, monitor):
        # make sure that the module is unloaded initially
        pytest.unload_dummy()
        monitor.filter_by('net')
        monitor.start()
        self.prepare_test(monitor)
        # setup signal handlers
        event_callback = mock.Mock(side_effect=self.stop_when_done)
        added_callback = mock.Mock(side_effect=self.stop_when_done)
        removed_callback = mock.Mock(side_effect=self.stop_when_done)
        self.connect_signal(event_callback)
        self.connect_signal(added_callback, action='add')
        self.connect_signal(removed_callback, action='remove')

        # test add event
        self.start_event_loop(pytest.load_dummy)
        device = Devices.from_path(context, '/devices/virtual/net/dummy0')
        event_callback.assert_called_with('add', device)
        added_callback.assert_called_with(device)
        assert not removed_callback.called

        for callback in (event_callback, added_callback, removed_callback):
            callback.reset_mock()

        self.start_event_loop(pytest.unload_dummy)
        event_callback.assert_called_with('remove', device)
        assert not added_callback.called
        removed_callback.assert_called_with(device)


class DeprecatedQtObserverTestBase(DeprecatedObserverTestBase):

    ACTION_SIGNAL_MAP = {
        'add': 'deviceAdded',
        'remove': 'deviceRemoved',
        'change': 'deviceChanged',
        'move': 'deviceMoved',
    }

    def setup(self):
        self.qtcore = pytest.importorskip('{0}.QtCore'.format(
            self.BINDING_NAME))

    def create_observer(self, monitor):
        name = self.BINDING_NAME.lower()
        mod = __import__('pyudev.{0}'.format(name), None, None, [name])
        self.observer = mod.QUDevMonitorObserver(monitor)

    def connect_signal(self, callback, action=None):
        if action is None:
            self.observer.deviceEvent.connect(callback)
        else:
            signal = getattr(self.observer, self.ACTION_SIGNAL_MAP[action])
            signal.connect(callback)

    def create_event_loop(self, self_stop_timeout=5000):
        self.app = self.qtcore.QCoreApplication.instance()
        if not self.app:
            self.app = self.qtcore.QCoreApplication([])
        self.qtcore.QTimer.singleShot(
            self_stop_timeout, self.stop_event_loop)

    def start_event_loop(self, start_callback):
        self.qtcore.QTimer.singleShot(0, start_callback)
        self.app.exec_()

    def stop_event_loop(self):
        self.app.quit()


class TestDeprecatedPysideObserver(DeprecatedQtObserverTestBase):
    BINDING_NAME = 'PySide'


class TestDeprecatedPyQt4Observer(DeprecatedQtObserverTestBase):
    BINDING_NAME = 'PyQt4'


class TestDeprecatedGlibObserver(DeprecatedObserverTestBase):

    ACTION_SIGNAL_MAP = {
        'add': 'device-added',
        'remove': 'device-removed',
        'change': 'device-changed',
        'move': 'device-moved',
    }

    def setup(self):
        self.event_sources = []
        self.glib = pytest.importorskip('glib')
        # make sure that we also have gobject
        pytest.importorskip('gobject')

    def teardown(self):
        for source in self.event_sources:
            self.glib.source_remove(source)

    def create_observer(self, monitor):
        from pyudev.glib import GUDevMonitorObserver
        self.observer = GUDevMonitorObserver(monitor)

    def connect_signal(self, callback, action=None):
        # drop the sender argument from glib signal connections
        def _wrapper(obj, *args, **kwargs):
            return callback(*args, **kwargs)
        if action is None:
            self.observer.connect('device-event', _wrapper)
        else:
            self.observer.connect(self.ACTION_SIGNAL_MAP[action], _wrapper)

    def create_event_loop(self, self_stop_timeout=5000):
        self.mainloop = self.glib.MainLoop()
        self.event_sources.append(
            self.glib.timeout_add(self_stop_timeout, self.stop_event_loop))

    def start_event_loop(self, start_callback):
        def _wrapper(*args, **kwargs):
            start_callback(*args, **kwargs)
            return False
        self.event_sources.append(self.glib.timeout_add(0, _wrapper))
        self.mainloop.run()

    def stop_event_loop(self):
        self.mainloop.quit()
        return False


@pytest.mark.skipif(str('"DISPLAY" not in os.environ'),
                    reason='Display required for wxPython')
class TestDeprecatedWxObserver(DeprecatedObserverTestBase):

    def setup(self):
        self.wx = pytest.importorskip('wx')

    def create_observer(self, monitor):
        from pyudev import wx
        self.observer = wx.WxUDevMonitorObserver(monitor)
        self.action_event_map = {
                'add': wx.EVT_DEVICE_ADDED,
                'remove': wx.EVT_DEVICE_REMOVED,
                'change': wx.EVT_DEVICE_CHANGED,
                'move': wx.EVT_DEVICE_MOVED
        }

    def connect_signal(self, callback, action=None):
        if action is None:
            from pyudev.wx import EVT_DEVICE_EVENT
            def _wrapper(event):
                return callback(event.action, event.device)
            self.observer.Bind(EVT_DEVICE_EVENT, _wrapper)
        else:
            def _wrapper(event):
                return callback(event.device)
            self.observer.Bind(self.action_event_map[action], _wrapper)

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
