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
    pyudev.pyqt4
    ============

    Provide :class:`~pyudev.pyqt4.QUDevMonitorObserver` to integrate a
    :class:`~pyudev.Monitor` into the Qt event loop in applications using the
    PyQt4_ binding to Qt.

    To use this module, :mod:`PyQt4.QtCore` from PyQt4_ must be available.

    .. _PyQt4: http://riverbankcomputing.co.uk/software/pyqt/intro

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""


from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from PyQt4.QtCore import QSocketNotifier, QObject, pyqtSignal

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

    This class is a child of :class:`~PyQt4.QtCore.QObject`.
    """

    #: emitted upon arbitrary device events
    deviceEvent = pyqtSignal(unicode, Device)
    #: emitted, if a device was added
    deviceAdded = pyqtSignal(Device)
    #: emitted, if a device was removed
    deviceRemoved = pyqtSignal(Device)
    #: emitted, if a device was changed
    deviceChanged = pyqtSignal(Device)
    #: emitted, if a device was moved
    deviceMoved = pyqtSignal(Device)

    def __init__(self, monitor, parent=None):
        """
        Observe the given ``monitor`` (a :class:`~pyudev.Monitor`):

        ``parent`` is the parent :class:`~PyQt4.QtCore.QObject` of this
        object.  It is passed unchanged to the inherited constructor of
        :class:`~PyQt4.QtCore.QObject`.
        """
        QObject.__init__(self, parent)
        self._setup_notifier(monitor, QSocketNotifier)
