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


import py.test
from mock import Mock


def pytest_generate_tests(metafunc):
    if 'action' in metafunc.funcargnames:
        for action in ('add', 'remove', 'change', 'move'):
            metafunc.addcall(funcargs=dict(action=action), id=action)


def test_fake_monitor(fake_monitor, platform_device):
    """
    Test the fake monitor just to make sure, that it works.
    """
    for action in ('add', 'remove'):
        fake_monitor.trigger_action(action)
        received_action, device = fake_monitor.receive_device()
        assert action == received_action
        assert device == platform_device


def _trigger_observer(action, monitor, action_trigger):
    QtCore = py.test.importorskip('PyQt4.QtCore')

    from qudev import QUDevMonitorObserver

    # our event loop
    app = QtCore.QCoreApplication([])
    # counts, how many signals were already emitted.  Used to exit the event
    # loop, once all expected signals were emitted
    signal_counter = QtCore.QSemaphore(2)

    def _quit_when_done(*args, **kwargs):
        signal_counter.acquire()
        if signal_counter.available() == 0:
            QtCore.QCoreApplication.instance().quit()

    # slot dummies
    event_slot = Mock(side_effect=_quit_when_done)
    action_slot = Mock(side_effect=_quit_when_done)

    # create the observer and connect the dummies
    observer = QUDevMonitorObserver(monitor)
    observer.deviceEvent.connect(event_slot)
    signal_map = {'add': observer.deviceAdded,
                  'remove': observer.deviceRemoved,
                  'change': observer.deviceChanged,
                  'move': observer.deviceMoved}
    signal_map[action].connect(action_slot)

    # trigger the action, once the event loop is running
    QtCore.QTimer.singleShot(0, action_trigger)

    # make sure, that the event loop really exits, even in case of an
    # exception in any python slot
    QtCore.QTimer.singleShot(5000, app.quit)
    app.exec_()
    return event_slot, action_slot


def test_observer_fake(action, fake_monitor, platform_device):
    event_slot, action_slot = _trigger_observer(
        action, fake_monitor, lambda: fake_monitor.trigger_action(action))
    # check, that both slots were called
    event_slot.assert_called_with(action, platform_device)
    action_slot.assert_called_with(platform_device)


@py.test.mark.skipif("not config.getvalue('allow_privileges')")
@py.test.mark.privileged
def test_observer(monitor):
    py.test.unload_dummy()
    monitor.filter_by('net')
    monitor.enable_receiving()
    event_slot, action_slot = _trigger_observer(
        'add', monitor, py.test.load_dummy)
    action, device = event_slot.call_args[0]
    assert action == 'add'
    assert device.subsystem == 'net'
    assert device.device_path == '/devices/virtual/net/dummy0'
    event_slot, action_slot = _trigger_observer(
        'remove', monitor, py.test.unload_dummy)
    action, device = event_slot.call_args[0]
    assert action == 'remove'
    assert device.subsystem == 'net'
    assert device.device_path == '/devices/virtual/net/dummy0'

