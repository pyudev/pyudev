# -*- coding: utf-8 -*-
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
    pyudev.pyqt5
    ============

    PyQt5 integration.

    :class:`MonitorObserver` integrates device monitoring into the PyQt5_
    mainloop by turning device events into Qt signals.

    :mod:`PyQt5.QtCore` from PyQt5_ must be available when importing this
    module.

    .. _gPyQt5: http://riverbankcomputing.co.uk/software/pyqt/intro

    .. moduleauthor::  Tobias Gehring  <mail@tobiasgehring.de>, Sebastian Wiesner  <lunaryorn@gmail.com>
"""


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QSocketNotifier

from pyudev.core import Device
from pyudev._qt_base import MonitorObserverMixin


class MonitorObserver(QObject, MonitorObserverMixin):
    """An observer for device events integrating into the :mod:`PyQt5` mainloop.

    This class inherits :class:`~PyQt5.QtCore.QObject` to turn device events
    into Qt signals:

    >>> from pyudev import Context, Monitor
    >>> from pyudev.pyqt5 import MonitorObserver
    >>> context = Context()
    >>> monitor = Monitor.from_netlink(context)
    >>> monitor.filter_by(subsystem='input')
    >>> observer = MonitorObserver(monitor)
    >>> def device_event(device):
    ...     print('event {0} on device {1}'.format(device.action, device))
    >>> observer.deviceEvent.connect(device_event)
    >>> monitor.start()

    This class is a child of :class:`~PyQt5.QtCore.QObject`.

    """

    #: emitted upon arbitrary device events
    deviceEvent = pyqtSignal(Device)

    def __init__(self, monitor, parent=None):
        """
        Observe the given ``monitor`` (a :class:`~pyudev.Monitor`):

        ``parent`` is the parent :class:`~PyQt5.QtCore.QObject` of this
        object.  It is passed unchanged to the inherited constructor of
        :class:`~PyQt5.QtCore.QObject`.
        """
        QObject.__init__(self, parent)
        self._setup_notifier(monitor, QSocketNotifier)
