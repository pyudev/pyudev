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
    pyudev.monitor
    ==============

    Monitor implementation.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""


from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import os
import select
from contextlib import closing

from pyudev._libudev import libudev, get_libudev_errno
from pyudev._util import assert_bytes, assert_unicode

from pyudev.core import Device


__all__ = ['Monitor']


class Monitor(object):
    """
    Monitor udev events:

    >>> context = pyudev.Context()
    >>> monitor = pyudev.Monitor.from_netlink(context)
    >>> monitor.filter_by(subsystem='input')
    >>> for action, device in monitor:
    ...     print('{0}: {1}'.format(action, device))
    ...

    A :class:`Monitor` objects connects to the udev daemon and listens for
    changes to the device list.  A monitor is created by connecting to the
    kernel daemon through netlink (see :meth:`from_netlink`).
    Alternatively, connections to arbitrary daemons can be made using
    :meth:`from_socket`, which is however only seldom of use.

    Once the monitor is created, you can add a filter using
    :meth:`filter_by` to drop incoming events in subsystems, which are not
    of interest to the application.

    If the monitor is eventually set up, you can either iterate over the
    :class:`Monitor` object.  In this case, the monitor implicitly starts
    listening, and polls for incoming events.  Such events are then yielded
    to the caller.  Iteration is a blocking operation and does not integrate
    into external event loops.  If such integration is required, you can
    explicitly enable the monitor (see :meth:`enable_receiving`), and then
    retrieve a file descriptor using :meth:`fileno`.  This file descriptor
    can then be passed to classes like
    :class:`~PyQt4.QtCore.QSocketNotifier` from Qt4.
    """

    def __init__(self, context, monitor_p, socket_path=None):
        self.context = context
        self._monitor = monitor_p
        self._socket_path = socket_path

    def __del__(self):
        libudev.udev_monitor_unref(self._monitor)

    @classmethod
    def from_netlink(cls, context, source='udev'):
        """
        Create a monitor by connecting to the kernel daemon through netlink.

        ``context`` is the :class:`Context` to use.  ``source`` is a string,
        describing the event source.  Two sources are available:

        ``'udev'`` (the default)
          Events emitted after udev as registered and configured the device.
          This is the absolutely recommended source for applications.

        ``'kernel'``
          Events emitted directly after the kernel has seen the device.  The
          device has not yet been configured by udev and might not be usable
          at all.  **Never** use this, unless you know what you are doing.

        Return a new :class:`Monitor` object, which is connected to the
        given source.  Raise :exc:`~exceptions.ValueError`, if an invalid
        source has been specified.  Raise
        :exc:`~exceptions.EnvironmentError`, if the creation of the monitor
        failed.
        """
        if source not in ('kernel', 'udev'):
            raise ValueError('Invalid source: {0!r}. Must be one of "udev" '
                             'or "kernel"'.format(source))
        source = assert_bytes(source)
        monitor = libudev.udev_monitor_new_from_netlink(
            context._context, source)
        if not monitor:
            raise EnvironmentError('Could not create udev monitor')
        return cls(context, monitor)

    @classmethod
    def from_socket(cls, context, socket_path):
        """
        Connect to an arbitrary udev daemon using the given ``socket_path``.

        ``context`` is the :class:`Context` to use. ``socket_path`` is a
        byte or unicode string, pointing to an existing socket.  If the path
        starts with a @, use an abstract namespace socket.  If
        ``socket_path`` does not exist, fall back to an abstract namespace
        socket.

        The caller is responsible for permissions and cleanup of the socket
        file.

        Return a new :class:`Monitor` object, which is connected to the
        given socket.  Raise :exc:`~exceptions.EnvironmentError`, if the
        creation of the monitor failed.
        """
        monitor = libudev.udev_monitor_new_from_socket(
            context._context, assert_bytes(socket_path))
        if not monitor:
            raise EnvironmentError('Could not create monitor for socket: '
                                   '{0!r}'.format(socket_path))
        return cls(context, monitor, socket_path=socket_path)

    def fileno(self):
        """
        Return the file description associated with this monitor as integer.

        This is really a real file descriptor ;), which can be watched and
        :func:`select.select`\ ed.
        """
        return libudev.udev_monitor_get_fd(self._monitor)

    def filter_by(self, subsystem, device_type=None):
        """
        Filter incoming events.

        ``subsystem`` is a byte or unicode string with the name of a
        subsystem (e.g. ``'input'``).  Only events originating from the
        given subsystem pass the filter and are handed to the caller.

        If given, ``device_type`` is a byte or unicode string specifying the
        device type.  Only devices with the given device type are propagated
        to the caller.  If ``device_type`` is not given, no additional
        filter for a specific device type is installed.

        These filters are executed inside the kernel, and client processes
        will usually not be woken up for device, that do not match these
        filters.

        This method must be called *before* :meth:`enable_receiving`.
        """
        subsystem = assert_bytes(subsystem)
        if device_type:
            device_type = assert_bytes(device_type)
        libudev.udev_monitor_filter_add_match_subsystem_devtype(
            self._monitor, subsystem, device_type)

    def enable_receiving(self):
        """
        Switch the monitor into listing mode.

        Connect to the event source and receive incoming events.  Only after
        calling this method, the monitor listens for incoming events.

        .. note::

           This method is implicitly called by :meth:`__iter__`.  You don't
           need to call it explicitly, if you are iterating over the
           monitor.
        """
        error = libudev.udev_monitor_enable_receiving(self._monitor)
        if error:
            errno = get_libudev_errno()
            raise EnvironmentError(errno, os.strerror(errno),
                                   self._socket_path)

    start = enable_receiving

    def receive_device(self):
        """
        Receive a single device from the monitor.

        The caller must make sure, that there are events available in the
        event queue.  The call blocks, until a device is available.

        If a device was available, return ``(action, device)``.  ``device``
        is the :class:`Device` object describing the device.  ``action`` is
        a string describing the action.  udev informs about the following
        actions:

        ``'add'``
          A device has been added (e.g. a USB device was plugged in)
        ``'remove'``
          A device has been removed (e.g. a USB device was unplugged)
        ``'change'``
          Something about the device changed (e.g. a device property)
        ``'move'``
          The device was renamed, moved, or re-parented

        Raise :exc:`~exceptions.EnvironmentError`, if no device could be
        read.
        """
        device_p = libudev.udev_monitor_receive_device(self._monitor)
        if not device_p:
            errno = get_libudev_errno()
            if errno == 0:
                raise EnvironmentError('Could not receive device')
            else:
                raise EnvironmentError(errno, os.strerror(errno))
        action = assert_unicode(libudev.udev_device_get_action(device_p))
        return action, Device(self.context, device_p)

    def __iter__(self):
        """
        Wait for incoming events and receive them upon arrival.

        This methods implicitly calls :meth:`enable_receiving`, and starts
        polling the :meth:`fileno` of this monitor.  If a event comes in, it
        receives the corresponding device and yields it to the caller.

        The returned iterator is endless, and continues receiving devices
        without ever stopping.

        Yields ``(action, device)`` (see :meth:`receive_device` for a
        description).
        """
        self.enable_receiving()
        with closing(select.epoll()) as notifier:
            notifier.register(self, select.EPOLLIN)
            while True:
                events = notifier.poll()
                if events:
                    yield self.receive_device()
