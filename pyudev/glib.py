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

"""
    pyudev.pygtk
    ============

    PyGtk binding for :mod:`pyudev`.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

# need absolute imports to import the glib binding module and not this
# module itself in the next lines
from __future__ import absolute_import

import glib
import gobject

from pyudev.core import Device


class GUDevMonitorObserver(gobject.GObject):
    """
    Observe a :class:`~pyudev.Monitor` and emit Glib signals upon device
    events:

    >>> context = pyudev.Context()
    >>> monitor = pyudev.Monitor.from_netlink(context)
    >>> monitor.filter_by(subsystem='input')
    >>> observer = pyudev.pygtk.GUDevMonitorObserver(monitor)
    >>> def device_connected(observer, device):
    ...     print('{0!r} added'.format(device))
    >>> observer.connect('device-added', device_connected)
    >>> monitor.start()

    This class is a child of :class:`gobject.GObject`.
    """

    _action_signal_map = {
        'add': 'device-added', 'remove': 'device-removed',
        'change': 'device-changed', 'move': 'device-moved'}

    __gsignals__ = {
        'device-event': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                         (gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)),
        'device-added': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                         (gobject.TYPE_PYOBJECT,)),
        'device-removed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                           (gobject.TYPE_PYOBJECT,)),
        'device-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                           (gobject.TYPE_PYOBJECT,)),
        'device-moved': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                         (gobject.TYPE_PYOBJECT,)),
        }

    def __init__(self, monitor):
        gobject.GObject.__init__(self)
        self.monitor = monitor
        self.event_source = glib.io_add_watch(monitor, glib.IO_IN,
                                              self._process_udev_event)

    def _process_udev_event(self, source, condition):
        if condition == glib.IO_IN:
            event = self.monitor.receive_device()
            if event:
                action, device = event
                self.emit('device-event', action, device)
                self.emit(self._action_signal_map[action], device)
        return True


gobject.type_register(GUDevMonitorObserver)
