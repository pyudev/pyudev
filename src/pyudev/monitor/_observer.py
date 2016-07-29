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
    pyudev.monitor._observer
    ========================

    Observe a monitor.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@gmail.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import select

from threading import Thread
from functools import partial

from pyudev._util import eintr_retry_call

from pyudev._os import pipe
from pyudev._os import poll

from pyudev._errors import DeviceMonitorError


class MonitorObserver(Thread):
    """
    An asynchronous observer for device events.

    This class subclasses :class:`~threading.Thread` class to asynchronously
    observe a :class:`Monitor` in a background thread:

    >>> from pyudev import Context, Monitor, MonitorObserver
    >>> context = Context()
    >>> monitor = Monitor.from_netlink(context)
    >>> monitor.filter_by(subsystem='input')
    >>> def print_device_event(device):
    ...     print('background event {0.action}: {0.device_path}'.format(device))
    >>> observer = MonitorObserver(monitor, callback=print_device_event, name='monitor-observer')
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

    .. seealso::

       :attr:`Device.action`
          The action that created this event.

       :attr:`Device.sequence_number`
          The sequence number of this event.

    .. versionadded:: 0.14

    .. versionchanged:: 0.15
       :meth:`Monitor.start()` is implicitly called when the thread is started.
    """

    def __init__(
        self,
        monitor,
        event_handler=None,
        callback=None,
        max_retries=0,
        *args,
        **kwargs
    ):
        """
        Create a new observer for the given ``monitor``.

        ``monitor`` is the :class:`Monitor` to observe. ``callback`` is the
        callable to invoke on events, with the signature ``callback(device)``
        where ``device`` is the :class:`Device` that caused the event.

        ``max_retries`` is the maximum number of times to read again from the
        buffer without getting an event before raising an exception. A value of
        None means that the Monitor will retry indefinitely. A value of 0 means
        that it will try only once to read an event. A negative value is
        unacceptable. The default is 0.

        .. warning::

           ``callback`` is invoked in the observer thread, hence the observer
           is blocked while callback executes.

        ``args`` and ``kwargs`` are passed unchanged to the constructor of
        :class:`~threading.Thread`.

        .. deprecated:: 0.16
           The ``event_handler`` argument will be removed in 1.0. Use
           the ``callback`` argument instead.
        .. versionchanged:: 0.16
           Add ``callback`` argument.
        """
        if callback is None and event_handler is None:
            raise ValueError('callback missing')
        elif callback is not None and event_handler is not None:
            raise ValueError('Use either callback or event handler')

        Thread.__init__(self, *args, **kwargs)
        self.monitor = monitor
        # observer threads should not keep the interpreter alive
        self.daemon = True
        self._stop_event = None
        if event_handler is not None:
            import warnings
            warnings.warn('"event_handler" argument will be removed in 1.0. '
                          'Use Monitor.poll() instead.', DeprecationWarning)
            callback = lambda d: event_handler(d.action, d)
        self._callback = callback
        self._max_retries = max_retries

    def start(self):
        """Start the observer thread."""
        if not self.is_alive():
            self._stop_event = pipe.Pipe.open()
        Thread.start(self)

    def _handle_monitor(self, fd, mask):
        """
        Handle a poll event on the monitor.

        :param fd: file descriptor for the monitor
        :param int event: the event mask (from select)

        :raises DeviceMonitorError: if mask does not include POLLIN
        """
        if mask & select.POLLIN != 0:
            read_device = partial(
               eintr_retry_call,
               self.monitor.poll,
               timeout=0,
               max_retries=self._max_retries
            )
            for device in iter(read_device, None):
                self._callback(device)
        else:
            raise DeviceMonitorError(
               "error when polling monitor device file descriptor (%d): %d" % \
               (fd, mask)
            )

    def run(self):
        """
        Run method for this thread.

        :raises DeviceMonitorError: if there is a problem with the Monitor
        """
        self.monitor.start()
        notifier = poll.Poll.for_events(self.monitor, self._stop_event.source)
        stop_event_fileno = self._stop_event.source.fileno()
        monitor_fileno = self.monitor.fileno()
        while True:
            for file_descriptor, event in eintr_retry_call(notifier.poll):
                if file_descriptor == stop_event_fileno:
                    # in case of a stop event, close our pipe side, and
                    # return from the thread
                    self._stop_event.source.close()
                    return
                elif file_descriptor == monitor_fileno:
                    self._handle_monitor(file_descriptor, event)

    def send_stop(self):
        """
        Send a stop signal to the background thread.

        The background thread will eventually exit, but it may still be running
        when this method returns.  This method is essentially the asynchronous
        equivalent to :meth:`stop()`.

        .. note::

           The underlying :attr:`monitor` is *not* stopped.
        """
        if self._stop_event is None:
            return
        with self._stop_event.sink:
            # emit a stop event to the thread
            eintr_retry_call(self._stop_event.sink.write, b'\x01')
            self._stop_event.sink.flush()

    def stop(self):
        """
        Synchronously stop the background thread.

        .. note::

           This method can safely be called from the observer thread. In this
           case it is equivalent to :meth:`send_stop()`.

        Send a stop signal to the backgroud (see :meth:`send_stop`), and waits
        for the background thread to exit (see :meth:`~threading.Thread.join`)
        if the current thread is *not* the observer thread.

        After this method returns in a thread *that is not the observer
        thread*, the ``callback`` is guaranteed to not be invoked again
        anymore.

        .. note::

           The underlying :attr:`monitor` is *not* stopped.

        .. versionchanged:: 0.16
           This method can be called from the observer thread.
        """
        self.send_stop()
        try:
            self.join()
        except RuntimeError:
            pass
