# -*- coding: utf-8 -*-
# Copyright (C) 2010, 2011 Sebastian Wiesner <lunaryorn@googlemail.com>

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
    pyudev.pyside
    =============

    Provide :class:`~pyudev.pyside.QUDevMonitorObserver` to integrate a
    :class:`~pyudev.Monitor` into the Qt event loop in applications using the
    PySide_ binding to Qt.

    To use this module, :mod:`PySide.QtCore` from PySide_ must be available.

    .. _PySide: http://www.pyside.org

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
    .. versionadded:: 0.6
"""


from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from PySide.QtCore import QSocketNotifier, QObject, Signal

from pyudev._qt_base import QUDevMonitorObserverMixin
from pyudev.core import Device


class QUDevMonitorObserver(QObject, QUDevMonitorObserverMixin):
    """
    Observe a :class:`~pyudev.Monitor` and emit Qt signals upon device
    events:

    >>> context = pyudev.Context()
    >>> monitor = pyudev.Monitor.from_netlink(context)
    >>> monitor.filter_by(subsystem='input')
    >>> observer = pyudev.pyqt4.QUDevMonitorObserver(monitor)
    >>> def device_connected(device):
    ...     print('{0!r} added'.format(device))
    >>> observer.deviceAdded.connect(device_connected)
    >>> monitor.start()

    This class is a child of :class:`~PySide.QtCore.QObject`.
    """

    #: emitted upon arbitrary device events
    deviceEvent = Signal(unicode, Device)
    #: emitted, if a device was added
    deviceAdded = Signal(Device)
    #: emitted, if a device was removed
    deviceRemoved = Signal(Device)
    #: emitted, if a device was changed
    deviceChanged = Signal(Device)
    #: emitted, if a device was moved
    deviceMoved = Signal(Device)

    def __init__(self, monitor, parent=None):
        """
        Observe the given ``monitor`` (a :class:`~pyudev.Monitor`):

        ``parent`` is the parent :class:`~PySide.QtCore.QObject` of this
        object.  It is passed unchanged to the inherited constructor of
        :class:`~PySide.QtCore.QObject`.
        """
        QObject.__init__(self, parent)
        self._setup_notifier(monitor, QSocketNotifier)
