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

# pylint: disable=anomalous-backslash-in-string

"""
    pyudev.pyqt4
    ============

    PyQt4 integration.

    :class:`MonitorObserver` integrates device monitoring into the PyQt4\_
    mainloop by turning device events into Qt signals.

    :mod:`PyQt4.QtCore` from PyQt4\_ must be available when importing this
    module.

    .. _PyQt4: http://riverbankcomputing.co.uk/software/pyqt/intro

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@gmail.com>
"""


from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from PyQt4.QtCore import QSocketNotifier, QObject, pyqtSignal

from pyudev._util import text_type
from pyudev.core import Device
from pyudev._qt_base import QUDevMonitorObserverMixin, MonitorObserverMixin


class MonitorObserver(QObject, MonitorObserverMixin):
    """An observer for device events integrating into the :mod:`PyQt4` mainloop.

    This class inherits :class:`~PyQt4.QtCore.QObject` to turn device events
    into Qt signals:

    >>> from pyudev import Context, Monitor
    >>> from pyudev.pyqt4 import MonitorObserver
    >>> context = Context()
    >>> monitor = Monitor.from_netlink(context)
    >>> monitor.filter_by(subsystem='input')
    >>> observer = MonitorObserver(monitor)
    >>> def device_event(device):
    ...     print('event {0} on device {1}'.format(device.action, device))
    >>> observer.deviceEvent.connect(device_event)
    >>> monitor.start()

    This class is a child of :class:`~PyQt4.QtCore.QObject`.

    """

    #: emitted upon arbitrary device events
    deviceEvent = pyqtSignal(Device)

    def __init__(self, monitor, parent=None):
        """
        Observe the given ``monitor`` (a :class:`~pyudev.Monitor`):

        ``parent`` is the parent :class:`~PyQt4.QtCore.QObject` of this
        object.  It is passed unchanged to the inherited constructor of
        :class:`~PyQt4.QtCore.QObject`.
        """
        QObject.__init__(self, parent)
        self._setup_notifier(monitor, QSocketNotifier)


class QUDevMonitorObserver(QObject, QUDevMonitorObserverMixin):
    """An observer for device events integrating into the :mod:`PyQt4` mainloop.

    .. deprecated:: 0.17
       Will be removed in 1.0.  Use :class:`MonitorObserver` instead.

    """

    #: emitted upon arbitrary device events
    deviceEvent = pyqtSignal(text_type, Device)
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
