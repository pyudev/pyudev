# -*- coding: utf-8 -*-
# Copyright (C) 2010, 2011, 2012, 2013, 2015 Sebastian Wiesner <lunaryorn@gmail.com>

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

"""pyudev.gi
    ===========

    gobject introspection (gi) integration.

    :class:`MonitorObserver` integrates device monitoring into the Glib
    mainloop by turing device events into Glib signals.

    :mod:`GLib` and :mod:`GObject` from gi_ must be available when
    importing this module.

    .. _PyGObject: https://wiki.gnome.org/PyGObject

    .. moduleauthor::  Adrián Pardini <github@tangopardo.com.ar>, Sebastian Wiesner  <lunaryorn@gmail.com>
    .. versionadded:: 0.17

"""


from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from gi.repository import GLib, GObject


class _ObserverMixin(object):
    """Mixin to provide observer behavior to the old and the new API."""

class MonitorObserver(GObject.GObject):
    """
    An observer for device events integrating into the :mod:`glib` mainloop.

    This class inherits :class:`~GObject.GObject` to turn device events into
    glib signals.

    >>> from pyudev import Context, Monitor
    >>> from pyudev.glib import MonitorObserver
    >>> context = Context()
    >>> monitor = Monitor.from_netlink(context)
    >>> monitor.filter_by(subsystem='input')
    >>> observer = MonitorObserver(monitor)
    >>> def device_event(observer, device):
    ...     print('event {0} on device {1}'.format(device.action, device))
    >>> observer.connect('device-event', device_event)
    >>> monitor.start()

    This class is a child of :class:`GObject.GObject`.
    """

    __gsignals__ = {
        # explicitly convert the signal to str, because glib expects the
        # *native* string type of the corresponding python version as type of
        # signal name, and str() is the name of the native string type of both
        # python versions.  We could also remove the "unicode_literals" import,
        # but I don't want to make exceptions to the standard set of future
        # imports used throughout pyudev for the sake of consistency.
        str('device-event'): (GObject.SignalFlags.RUN_LAST, GObject.TYPE_NONE,
                              (GObject.TYPE_PYOBJECT,)),
    }

    def __init__(self, monitor):
        GObject.GObject.__init__(self)
        self.monitor = monitor
        self.event_source = None
        self.enabled = True
    
    @property
    def enabled(self):
        """
        Whether this observer is enabled or not.

        If ``True`` (the default), this observer is enabled, and emits events.
        Otherwise it is disabled and does not emit any events.
        """
        return self.event_source is not None

    @enabled.setter
    def enabled(self, value):
        if value and self.event_source is None:
            self.event_source = GLib.io_add_watch(
                self.monitor, GLib.IOCondition.IN, self._process_udev_event)
        elif not value and self.event_source is not None:
            GLib.source_remove(self.event_source)

    def _process_udev_event(self, source, condition):
        if condition == GLib.IOCondition.IN:
            device = self.monitor.poll(timeout=0)
            if device:
                self._emit_event(device)
        return True

    def _emit_event(self, device):
        self.emit('device-event', device)




GObject.type_register(MonitorObserver)


