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

from itertools import count
from functools import partial

import pytest
from mock import Mock

class BaseBinding(object):
    def trigger_observer(self, action, monitor, action_trigger):
        mainloop = self.create_mainloop()

        signal_counter = count(1)

        def _quit_when_done(*args, **kwargs):
            value = next(signal_counter)
            if value >= 2:
                self.quit_mainloop(mainloop)

        # slot dummies
        event_slot = Mock(side_effect=_quit_when_done)
        action_slots = {action: Mock(side_effect=_quit_when_done)}
        observer = self.create_observer(monitor)
        self.connect_signals(observer, event_slot, action_slots)

        self.single_shot(0, action_trigger)
        self.single_shot(5000, partial(self.quit_mainloop, mainloop))
        self.run_mainloop(mainloop)
        self.cleanup(observer)
        return event_slot, action_slots


class Qt4Binding(BaseBinding):

    def __init__(self, bindingname):
        self.name = bindingname

    def create_observer(self, monitor):
        name = self.name.lower()
        mod = __import__('pyudev.{0}'.format(name), None, None, [name])
        observer = mod.QUDevMonitorObserver(monitor)
        assert observer.monitor is monitor
        assert isinstance(observer.notifier, self.qtcore.QSocketNotifier)
        return observer

    def import_or_skip(self):
        self.qtcore = pytest.importorskip('{0}.QtCore'.format(self.name))

    def create_mainloop(self):
        app = self.qtcore.QCoreApplication.instance()
        if not app:
            app = self.qtcore.QCoreApplication([])
        return app

    def quit_mainloop(self, app):
        app.quit()

    def run_mainloop(self, app):
        app.exec_()

    def connect_signals(self, observer, event_slot, action_slots):
        observer.deviceEvent.connect(event_slot)
        signal_map = {'add': observer.deviceAdded,
                      'remove': observer.deviceRemoved,
                      'change': observer.deviceChanged,
                      'move': observer.deviceMoved}
        for action, slot in action_slots.items():
            signal_map[action].connect(slot)

    def single_shot(self, timeout, callback):
        self.qtcore.QTimer.singleShot(timeout, callback)

    def cleanup(self, observer):
        observer.enabled = False


class GlibBinding(BaseBinding):
    name = 'Glib'

    def __init__(self):
        self.event_sources = []

    def create_observer(self, monitor):
        from pyudev.glib import GUDevMonitorObserver
        observer = GUDevMonitorObserver(monitor)
        assert observer.monitor is monitor
        assert isinstance(observer.event_source, int)
        return observer

    def import_or_skip(self):
        self.glib = pytest.importorskip('glib')
        pytest.importorskip('gobject')

    def create_mainloop(self):
        return self.glib.MainLoop()

    def quit_mainloop(self, mainloop):
        mainloop.quit()

    def run_mainloop(self, mainloop):
        mainloop.run()

    def wrap_callback(self, callback):
        """
        Remove the emitter from callback invocation, it is not of any
        interest to the test code.
        """
        def _wrapper(obj, *args, **kwargs):
            return callback(*args, **kwargs)
        return _wrapper

    def connect_signals(self, observer, event_slot, action_slots):
        observer.connect('device-event', self.wrap_callback(event_slot))
        signal_map = {'add': 'device-added', 'remove': 'device-removed',
                      'change': 'device-changed', 'move': 'device-moved'}
        for action, slot in action_slots.items():
            observer.connect(signal_map[action], self.wrap_callback(slot))

    def single_shot(self, timeout, callback):
        def _callback():
            callback()
            return False
        self.event_sources.append(self.glib.timeout_add(timeout, _callback))

    def cleanup(self, observer):
        observer.enabled = False
        # cleanup all timer event sources.  If this was not done, all tests
        # save the first would spin endlessly.  Apparently older event sources
        # kind of "confuse" the main loop of the current test
        for source in self.event_sources:
            self.glib.source_remove(source)
        self.event_sources = []


class WXBinding(BaseBinding):
    name = 'wx'

    timer = []

    def create_observer(self, monitor):
        from pyudev.wx import WxUDevMonitorObserver
        observer = WxUDevMonitorObserver(monitor)
        assert observer.monitor is monitor
        return observer

    def import_or_skip(self):
        self.wx = pytest.importorskip('wx')

    def create_mainloop(self):
        app = self.wx.App(False)
        app.frame = self.wx.Frame(None)
        self.frame = app.frame
        return app

    def quit_mainloop(self, app):
        app.frame.Close()

    def run_mainloop(self, app):
        app.MainLoop()

    def connect_signals(self, observer, event_slot, action_slots):
        def wrap_callback(callback):
            def _wrapper(event):
                if (hasattr(event, 'action')):
                    return callback(event.action, event.device)
                else:
                    return callback(event.device)
            return _wrapper

        import pyudev.wx
        observer.Bind(pyudev.wx.EVT_DEVICE_EVENT, wrap_callback(event_slot))
        event_map = {
                'add': pyudev.wx.EVT_DEVICE_ADDED,
                'remove': pyudev.wx.EVT_DEVICE_REMOVED,
                'change': pyudev.wx.EVT_DEVICE_CHANGED,
                'move': pyudev.wx.EVT_DEVICE_MOVED }
        for action, slot in action_slots.items():
            observer.Bind(event_map[action], wrap_callback(slot))

    def single_shot(self, timeout, callback):
        timer = self.wx.PyTimer(callback)
        self.timer.append(timer)
        timer.Start(timeout, True)

    def cleanup(self, observer):
        # disable the observer to avoid that some pending observers confuse our
        # tests
        observer.enabled = False


BINDINGS = [Qt4Binding('PyQt4'), Qt4Binding('PySide'), GlibBinding(), WXBinding()]
ACTIONS = ('add', 'remove', 'change', 'move')


def pytest_generate_tests(metafunc):
    if 'binding' in metafunc.funcargnames:
        for binding in BINDINGS:
            funcargs = dict(binding=binding)
            id = binding.name
            if 'action' in metafunc.funcargnames:
                for action in ACTIONS:
                    funcargs.update(action=action)
                    metafunc.addcall(funcargs=funcargs,
                                     id=id + ',' + action)
            else:
                metafunc.addcall(funcargs=funcargs, id=id)


def test_fake_monitor(fake_monitor, platform_device):
    """
    Test the fake monitor just to make sure, that it works.
    """
    for action in ('add', 'remove'):
        fake_monitor.trigger_action(action)
        received_action, device = fake_monitor.receive_device()
        assert action == received_action
        assert device == platform_device


class TestObserver(object):

    def test_observer_fake(self, binding, action, fake_monitor,
                           platform_device):
        binding.import_or_skip()
        event_slot, action_slots = binding.trigger_observer(
            action, fake_monitor, lambda: fake_monitor.trigger_action(action))
        # check, that both slots were called
        event_slot.assert_called_with(action, platform_device)
        action_slots.pop(action).assert_called_with(platform_device)

    @pytest.mark.privileged
    def test_observer(self, binding, monitor):
        binding.import_or_skip()
        pytest.unload_dummy()
        monitor.filter_by('net')
        monitor.enable_receiving()
        event_slot, action_slot = binding.trigger_observer(
            'add', monitor, pytest.load_dummy)
        action, device = event_slot.call_args[0]
        assert action == 'add'
        assert device.subsystem == 'net'
        assert device.device_path == '/devices/virtual/net/dummy0'
        event_slot, action_slot = binding.trigger_observer(
            'remove', monitor, pytest.unload_dummy)
        action, device = event_slot.call_args[0]
        assert action == 'remove'
        assert device.subsystem == 'net'
        assert device.device_path == '/devices/virtual/net/dummy0'
