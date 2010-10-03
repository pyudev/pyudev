# -*- coding: utf-8 -*-
# Copyright (C) 2010 Sebastian Wiesner <lunaryorn@googlemail.com>

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


import py.test
from mock import Mock


class Binding(object):
    def __init__(self, bindingname):
        self.name = bindingname

    @property
    def observer_class(self):
        name = self.name.lower()
        binding = __import__('pyudev.{0}'.format(name), None, None, [name])
        return binding.QUDevMonitorObserver

    @property
    def qtcore(self):
        return py.test.importorskip('{0}.QtCore'.format(self.name))


BINDINGS = [Binding('PyQt4'), Binding('PySide')]
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


def _trigger_observer(binding, action, monitor, action_trigger):
    # try to get an existing event loop, if there is one, or otherwise
    # create a new one
    app = binding.qtcore.QCoreApplication.instance()
    if not app:
        app = binding.qtcore.QCoreApplication([])

    # counts, how many signals were already emitted.  Used to exit the event
    # loop, once all expected signals were emitted
    signal_counter = binding.qtcore.QSemaphore(2)

    def _quit_when_done(*args, **kwargs):
        signal_counter.acquire()
        if signal_counter.available() == 0:
            # we got all expected signals, so jump out of event loop to
            # continue sequential test running
            binding.qtcore.QCoreApplication.instance().quit()

    # slot dummies
    event_slot = Mock(side_effect=_quit_when_done)
    action_slot = Mock(side_effect=_quit_when_done)

    # create the observer and connect the dummies
    observer = binding.observer_class(monitor)
    observer.deviceEvent.connect(event_slot)
    signal_map = {'add': observer.deviceAdded,
                  'remove': observer.deviceRemoved,
                  'change': observer.deviceChanged,
                  'move': observer.deviceMoved}
    signal_map[action].connect(action_slot)

    # trigger the action, once the event loop is running
    binding.qtcore.QTimer.singleShot(0, action_trigger)

    # make sure, that the event loop really exits, even in case of an
    # exception in any python slot
    binding.qtcore.QTimer.singleShot(5000, app.quit)
    app.exec_()
    return event_slot, action_slot


def test_observer_fake(binding, action, fake_monitor, platform_device):
    event_slot, action_slot = _trigger_observer(
        binding, action, fake_monitor,
        lambda: fake_monitor.trigger_action(action))
    # check, that both slots were called
    event_slot.assert_called_with(action, platform_device)
    action_slot.assert_called_with(platform_device)


@py.test.mark.privileged
def test_observer(binding, monitor):
    py.test.unload_dummy()
    monitor.filter_by('net')
    monitor.enable_receiving()
    event_slot, action_slot = _trigger_observer(
        binding, 'add', monitor, py.test.load_dummy)
    action, device = event_slot.call_args[0]
    assert action == 'add'
    assert device.subsystem == 'net'
    assert device.device_path == '/devices/virtual/net/dummy0'
    event_slot, action_slot = _trigger_observer(
        binding, 'remove', monitor, py.test.unload_dummy)
    action, device = event_slot.call_args[0]
    assert action == 'remove'
    assert device.subsystem == 'net'
    assert device.device_path == '/devices/virtual/net/dummy0'

