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


"""
    pyudev.monitor._monitor
    =======================

    Monitor implementation.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@gmail.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import errno

from pyudev.device import Device

from pyudev._util import eintr_retry_call
from pyudev._util import ensure_byte_string

from pyudev._os import pipe
from pyudev._os import poll


class Monitor(object):
    """
    A synchronous device event monitor.

    A :class:`Monitor` objects connects to the udev daemon and listens for
    changes to the device list.  A monitor is created by connecting to the
    kernel daemon through netlink (see :meth:`from_netlink`):

    >>> from pyudev import Context, Monitor
    >>> context = Context()
    >>> monitor = Monitor.from_netlink(context)

    Once the monitor is created, you can add a filter using :meth:`filter_by()`
    or :meth:`filter_by_tag()` to drop incoming events in subsystems, which are
    not of interest to the application:

    >>> monitor.filter_by('input')

    When the monitor is eventually set up, you can either poll for events
    synchronously:

    >>> device = monitor.poll(timeout=3)
    >>> if device:
    ...     print('{0.action}: {0}'.format(device))
    ...

    Or you can monitor events asynchronously with :class:`MonitorObserver`.

    To integrate into various event processing frameworks, the monitor provides
    a :func:`selectable <select.select>` file description by :meth:`fileno()`.
    However, do *not*  read or write directly on this file descriptor.

    Instances of this class can directly be given as ``udev_monitor *`` to
    functions wrapped through :mod:`ctypes`.

    .. versionchanged:: 0.16
       Remove :meth:`from_socket()` which is deprecated, and even removed in
       recent udev versions.
    """

    def __init__(self, context, monitor_p):
        self.context = context
        self._as_parameter_ = monitor_p
        self._libudev = context._libudev
        self._started = False

    def __del__(self):
        self._libudev.udev_monitor_unref(self)

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
        monitor = context._libudev.udev_monitor_new_from_netlink(
            context, ensure_byte_string(source))
        if not monitor:
            raise EnvironmentError('Could not create udev monitor')
        return cls(context, monitor)

    @property
    def started(self):
        """
        ``True``, if this monitor was started, ``False`` otherwise. Readonly.

        .. seealso:: :meth:`start()`
        .. versionadded:: 0.16
        """
        return self._started

    def fileno(self):
        # pylint: disable=anomalous-backslash-in-string
        """
        Return the file description associated with this monitor as integer.

        This is really a real file descriptor ;), which can be watched and
        :func:`select.select`\ ed.
        """
        return self._libudev.udev_monitor_get_fd(self)

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

        .. versionchanged:: 0.15
           This method can also be after :meth:`start()` now.
        """
        subsystem = ensure_byte_string(subsystem)
        if device_type is not None:
            device_type = ensure_byte_string(device_type)
        self._libudev.udev_monitor_filter_add_match_subsystem_devtype(
            self, subsystem, device_type)
        self._libudev.udev_monitor_filter_update(self)

    def filter_by_tag(self, tag):
        """
        Filter incoming events by the given ``tag``.

        ``tag`` is a byte or unicode string with the name of a tag.  Only
        events for devices which have this tag attached pass the filter and are
        handed to the caller.

        Like with :meth:`filter_by` this filter is also executed inside the
        kernel, so that client processes are usually not woken up for devices
        without the given ``tag``.

        .. udevversion:: 154

        .. versionadded:: 0.9

        .. versionchanged:: 0.15
           This method can also be after :meth:`start()` now.
        """
        self._libudev.udev_monitor_filter_add_match_tag(
            self, ensure_byte_string(tag))
        self._libudev.udev_monitor_filter_update(self)

    def remove_filter(self):
        """
        Remove any filters installed with :meth:`filter_by()` or
        :meth:`filter_by_tag()` from this monitor.

        .. warning::

           Up to udev 181 (and possibly even later versions) the underlying
           ``udev_monitor_filter_remove()`` seems to be broken.  If used with
           affected versions this method always raises
           :exc:`~exceptions.ValueError`.

        Raise :exc:`~exceptions.EnvironmentError` if removal of installed
        filters failed.

        .. versionadded:: 0.15
        """
        self._libudev.udev_monitor_filter_remove(self)
        self._libudev.udev_monitor_filter_update(self)

    def enable_receiving(self):
        """
        Switch the monitor into listing mode.

        Connect to the event source and receive incoming events.  Only after
        calling this method, the monitor listens for incoming events.

        .. note::

           This method is implicitly called by :meth:`__iter__`.  You don't
           need to call it explicitly, if you are iterating over the
           monitor.

        .. deprecated:: 0.16
           Will be removed in 1.0. Use :meth:`start()` instead.
        """
        import warnings
        warnings.warn('Will be removed in 1.0. Use Monitor.start() instead.',
                      DeprecationWarning)
        self.start()

    def start(self):
        """
        Start this monitor.

        The monitor will not receive events until this method is called. This
        method does nothing if called on an already started :class:`Monitor`.

        .. note::

           Typically you don't need to call this method. It is implicitly
           called by :meth:`poll()` and :meth:`__iter__()`.

        .. seealso:: :attr:`started`
        .. versionchanged:: 0.16
           This method does nothing if the :class:`Monitor` was already
           started.
        """
        if not self._started:
            self._libudev.udev_monitor_enable_receiving(self)
            # Force monitor FD into non-blocking mode
            pipe.set_fd_status_flag(self, os.O_NONBLOCK)
            self._started = True

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
        self._libudev.udev_monitor_set_receive_buffer_size(self, size)

    def _receive_device(self):
        """Receive a single device from the monitor.

        Return the received :class:`Device`, or ``None`` if no device could be
        received.

        """
        while True:
            try:
                device_p = self._libudev.udev_monitor_receive_device(self)
                return Device(self.context, device_p) if device_p else None
            except EnvironmentError as error:
                if error.errno in (errno.EAGAIN, errno.EWOULDBLOCK):
                    # No data available
                    return None
                elif error.errno == errno.EINTR:
                    # Try again if our system call was interrupted
                    continue
                else:
                    raise

    def poll(self, timeout=None):
        """
        Poll for a device event.

        You can use this method together with :func:`iter()` to synchronously
        monitor events in the current thread::

           for device in iter(monitor.poll, None):
               print('{0.action} on {0.device_path}'.format(device))

        Since this method will never return ``None`` if no ``timeout`` is
        specified, this is effectively an endless loop. With
        :func:`functools.partial()` you can also create a loop that only waits
        for a specified time::

           for device in iter(partial(monitor.poll, 3), None):
               print('{0.action} on {0.device_path}'.format(device))

        This loop will only wait three seconds for a new device event. If no
        device event occurred after three seconds, the loop will exit.

        ``timeout`` is a floating point number that specifies a time-out in
        seconds. If omitted or ``None``, this method blocks until a device
        event is available. If ``0``, this method just polls and will never
        block.

        .. note::

           This method implicitly calls :meth:`start()`.

        Return the received :class:`Device`, or ``None`` if a timeout
        occurred. Raise :exc:`~exceptions.EnvironmentError` if event retrieval
        failed.

        .. seealso::

           :attr:`Device.action`
              The action that created this event.

           :attr:`Device.sequence_number`
              The sequence number of this event.

        .. versionadded:: 0.16
        """
        if timeout is not None and timeout > 0:
            # .poll() takes timeout in milliseconds
            timeout = int(timeout * 1000)
        self.start()

        events = eintr_retry_call(poll.Poll.for_events(self).poll, timeout)
        if events == []:
            return None
        else:
            return self._receive_device()

    def receive_device(self):
        """
        Receive a single device from the monitor.

        .. warning::

           You *must* call :meth:`start()` before calling this method.

        The caller must make sure, that there are events available in the
        event queue.  The call blocks, until a device is available.

        If a device was available, return ``(action, device)``.  ``device``
        is the :class:`Device` object describing the device.  ``action`` is
        a string describing the action.  Usual actions are:

        ``'add'``
          A device has been added (e.g. a USB device was plugged in)
        ``'remove'``
          A device has been removed (e.g. a USB device was unplugged)
        ``'change'``
          Something about the device changed (e.g. a device property)
        ``'online'``
          The device is online now
        ``'offline'``
          The device is offline now

        Raise :exc:`~exceptions.EnvironmentError`, if no device could be
        read.

        .. deprecated:: 0.16
           Will be removed in 1.0. Use :meth:`Monitor.poll()` instead.
        """
        import warnings
        warnings.warn('Will be removed in 1.0. Use Monitor.poll() instead.',
                      DeprecationWarning)
        device = self.poll()
        return device.action, device

    def __iter__(self):
        """
        Wait for incoming events and receive them upon arrival.

        This methods implicitly calls :meth:`start()`, and starts polling the
        :meth:`fileno` of this monitor.  If a event comes in, it receives the
        corresponding device and yields it to the caller.

        The returned iterator is endless, and continues receiving devices
        without ever stopping.

        Yields ``(action, device)`` (see :meth:`receive_device` for a
        description).

        .. deprecated:: 0.16
           Will be removed in 1.0. Use an explicit loop over :meth:`poll()`
           instead, or monitor asynchronously with :class:`MonitorObserver`.
        """
        import warnings
        warnings.warn('Will be removed in 1.0. Use an explicit loop over '
                      '"poll()" instead, or monitor asynchronously with '
                      '"MonitorObserver".', DeprecationWarning)
        self.start()
        while True:
            device = self.poll()
            if device is not None:
                yield device.action, device
