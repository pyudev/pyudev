# -*- coding: utf-8 -*-
# Copyright (C) 2010, 2011, 2012 Sebastian Wiesner <lunaryorn@googlemail.com>

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
import sys
import select
from threading import Thread
from contextlib import closing

from pyudev._libudev import libudev
from pyudev._util import ensure_byte_string, ensure_unicode_string, reraise

from pyudev.core import Device


__all__ = ['Monitor', 'MonitorObserver']


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

    Instances of this class can directly be given as ``udev_monitor *`` to
    functions wrapped through :mod:`ctypes`.
    """

    def __init__(self, context, monitor_p, socket_path=None):
        self.context = context
        self._as_parameter_ = monitor_p
        self._socket_path = socket_path

    def _reraise_with_socket_path(self):
        _, exc_value, traceback = sys.exc_info()
        exc_value.filename = self._socket_path
        reraise(exc_value, traceback)

    def __del__(self):
        libudev.udev_monitor_unref(self)

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
        monitor = libudev.udev_monitor_new_from_netlink(
            context, ensure_byte_string(source))
        if not monitor:
            raise EnvironmentError('Could not create udev monitor')
        return cls(context, monitor)

    @classmethod
    def from_socket(cls, context, socket_path):
        """
        Connect to an arbitrary udev daemon using the given ``socket_path``.

        ``context`` is the :class:`Context` to use. ``socket_path`` is a byte
        or unicode string, pointing to an existing socket.  If the path starts
        with a ``@``, use an abstract namespace socket.  If ``socket_path``
        does not exist, fall back to an abstract namespace socket.

        The caller is responsible for permissions and cleanup of the socket
        file.

        Return a new :class:`Monitor` object, which is connected to the given
        socket.  Raise :exc:`~exceptions.EnvironmentError`, if the creation of
        the monitor failed.
        """
        monitor = libudev.udev_monitor_new_from_socket(
            context, ensure_byte_string(socket_path))
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
        return libudev.udev_monitor_get_fd(self)

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
        subsystem = ensure_byte_string(subsystem)
        if device_type:
            device_type = ensure_byte_string(device_type)
        libudev.udev_monitor_filter_add_match_subsystem_devtype(
            self, subsystem, device_type)

    def filter_by_tag(self, tag):
        """
        Filter incoming events by the given ``tag``.

        ``tag`` is a byte or unicode string with the name of a tag.  Only
        events for devices which have this tag attached pass the filter and are
        handed to the caller.

        Like with :meth:`filter_by` this filter is also executed inside the
        kernel, so that client processes are usually not woken up for devices
        without the given ``tag``.

        This method must be called *before* :meth:`enable_receiving`.

        .. udevversion:: 154

        .. versionadded:: 0.9
        """
        libudev.udev_monitor_filter_add_match_tag(
            self, ensure_byte_string(tag))

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
        try:
            libudev.udev_monitor_enable_receiving(self)
        except EnvironmentError:
            self._reraise_with_socket_path()

    start = enable_receiving

    def set_receive_buffer_size(self, size):
        """
        Set the receive buffer ``size``.

        ``size`` is the requested buffer size in bytes, as integer.

        .. note::

           The CAP_NET_ADMIN capability must be contained in the effective
           capability set of the caller for this method to succeed.  Otherwise
           :exc:`~exceptions.EnvironmentError` will be raised, with ``errno``
           set to :data:`~errno.EPERM`.  Unprivileged processes typically lack
           this capability.  You can check the capabilities of the current
           process with the python-prctl_ module:

           >>> import prctl
           >>> prctl.cap_effective.net_admin

        Raise :exc:`~exceptions.EnvironmentError`, if the buffer size could not
        bet set.

        .. versionadded:: 0.13

        .. _python-prctl: http://packages.python.org/python-prctl
        """
        try:
            libudev.udev_monitor_set_receive_buffer_size(self, size)
        except EnvironmentError:
            self._reraise_with_socket_path()

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
        try:
            device_p = libudev.udev_monitor_receive_device(self)
        except EnvironmentError:
            self._reraise_with_socket_path()
        if not device_p:
            raise EnvironmentError('Could not receive device')
        action = ensure_unicode_string(
            libudev.udev_device_get_action(device_p))
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
                for event in events:
                    yield self.receive_device()


class MonitorObserver(Thread):
    """
    A :class:`~threading.Thread` class to observe a :class:`Monitor` in background:

    >>> context = pyudev.Context()
    >>> monitor = pyudev.Monitor.from_netlink(context)
    >>> monitor.filter_by(subsystem='input')
    >>> def print_device_event(action, device):
    ...     print('background event {0}: {1}'.format(action, device))
    >>> observer = MonitorObserver(monitor, print_device_event, name='monitor-observer')
    >>> observer.daemon
    True
    >>> observer.start()

    In the above example, input device events will be printed in background,
    until :meth:`stop()` is called on ``observer``.

    .. note::

      Instances of this class are always created as daemon thread.  If you do
      not want to use daemon threads for monitoring, you need explicitly set
      :attr:`~threading.Thread.daemon` to ``False`` before invoking
      :meth:`~threading.Thread.start()`.
    """

    def __init__(self, monitor, event_handler, *args, **kwargs):
        """
        Create a new observer for the given ``monitor``.

        ``monitor`` is the :class:`Monitor` to observe.  ``event_handler`` is a
        callable with the signature ``event_handler(action, device)``, where
        ``action`` is a string describing the event (see
        :meth:`Monitor.receive_device`), and ``device`` is the :class:`Device`
        object that caused this event.  This callable is invoked for every
        device event received through ``monitor``.

        .. warning::

           ``event_handler`` is always invoked in this background thread, and
           *not* in the calling thread.

        ``args`` and ``kwargs`` are passed unchanged to the parent constructor
        of :class:`~threading.Thread`.
        """
        Thread.__init__(self, *args, **kwargs)

        self.monitor = monitor
        # observer threads should not keep the interpreter alive
        self.daemon = True
        self._stop_event_source, self._stop_event_sink = os.pipe()
        self._handle_event = event_handler

    def run(self):
        with closing(select.epoll()) as notifier:
            # poll on the stop event fd
            notifier.register(self._stop_event_source, select.EPOLLIN)
            # and on the monitor
            notifier.register(self.monitor, select.EPOLLIN)
            while True:
                for fd, _ in notifier.poll():
                    if fd == self._stop_event_source:
                        # in case of a stop event, close our pipe side, and
                        # return from the thread
                        os.close(self._stop_event_source)
                        return
                    else:
                        event = self.monitor.receive_device()
                        if event:
                            action, device = event
                            self._handle_event(action, device)

    def send_stop(self):
        """
        Send a stop signal to the background thread.

        The background thread will eventually exit, but it may still be running
        when this method returns.  This method is essentially the asynchronous
        equivalent to :meth:`stop()`.

        .. note::

           The underlying :attr:`monitor` is *not* stopped.
        """
        if self._stop_event_sink is None:
            return
        try:
            # emit a stop event to the thread
            os.write(self._stop_event_sink, b'\x01')
        finally:
            # close the out-of-thread side of the pipe
            os.close(self._stop_event_sink)
            self._stop_event_sink = None

    def stop(self):
        """
        Stop the background thread.

        .. warning::

           Calling this method from the ``event_handler`` results in a dead
           lock.  If you need to stop the observer from ``event_handler``, use
           :meth:`send_stop`, and be prepared to get some more events before
           the observer actually exits.

        Send a stop signal to the backgroud (see :meth:`send_stop`) and waits
        for the background thread to exit (see :meth:`~threading.Thread.join`).
        After this method returns, it is guaranteed that the ``event_handler``
        passed to :meth:`MonitorObserver.__init__()` is not longer called for
        any event from :attr:`monitor`.

        .. note::

           The underlying :attr:`monitor` is *not* stopped.
        """
        self.send_stop()
        self.join()
