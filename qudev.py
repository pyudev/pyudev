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

"""
    qudev
    =====

    PyQt4 binding for :mod:`udev`.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""


from PyQt4.QtCore import QSocketNotifier, QObject, pyqtSignal

import udev


class QUDevMonitorObserver(QObject):
    """
    Observe a :class:`udev.Monitor` and emit Qt signals upon device events:

    >>> context.Context()
    >>> monitor = Monitor.from_netlink(context)
    >>> monitor.filter_by(subsystem='input')
    >>> observer = QUDevMonitorObserver(monitor)
    >>> observer.deviceAdded.connect(
    ...     lambda device: print('{0!r} added'.format(device)))
    >>> monitor.start()
    """

    #: emitted upon arbitrary device events
    deviceEvent = pyqtSignal(unicode, udev.Device)
    #: emitted, if a device was added
    deviceAdded = pyqtSignal(udev.Device)
    #: emitted, if a device was removed
    deviceRemoved = pyqtSignal(udev.Device)
    #: emitted, if a device was changed
    deviceChanged = pyqtSignal(udev.Device)
    #: emitted, if a device was moved
    deviceMoved = pyqtSignal(udev.Device)


    def __init__(self, monitor, parent=None):
        """
        Observe the given ``monitor`` (a :class:`udev.Monitor`):

        ``parent`` is the parent QObject of this object.  It is passed
        unchanged to the inherited constructor of QObject.
        """
        QObject.__init__(self, parent)
        self.monitor = monitor
        self.notifier = QSocketNotifier(
            monitor.fileno(), QSocketNotifier.Read, self)
        self.notifier.activated[int].connect(self._process_udev_event)
        self._action_signal_map = {
            'add': self.deviceAdded, 'remove': self.deviceRemoved,
            'change': self.deviceChanged, 'move': self.deviceMoved,
        }


    def _process_udev_event(self):
        """
        Attempt to receive a single device event from the monitor, process
        the event and emit corresponding signals.

        Called by :class:`~PyQt4.QtCore.QSocketNotifier`, if data is
        available on the udev monitoring socket.
        """
        event = self.monitor.receive_device()
        if event:
            action, device = event
            self.deviceEvent.emit(action, device)
            self._action_signal_map[action].emit(device)
