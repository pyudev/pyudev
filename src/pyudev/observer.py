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
    pyudev.observer
    ==============

    MonitorObserver implementation

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@gmail.com>
"""


from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from threading import Thread
from functools import partial

from pyudev._errors import DeviceMonitorError

from pyudev._util import eintr_retry_call

from pyudev._os import pipe
from pyudev._os import poll


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

    def __init__(self, monitor, event_handler=None, callback=None, *args,
                 **kwargs):
        """
        Create a new observer for the given ``monitor``.

        ``monitor`` is the :class:`Monitor` to observe. ``callback`` is the
        callable to invoke on events, with the signature ``callback(device)``
        where ``device`` is the :class:`Device` that caused the event.

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

    def start(self):
        """Start the observer thread."""
        if not self.is_alive():
            self._stop_event = pipe.Pipe.open()
        Thread.start(self)

    def run(self):
        """
        Observe the monitor.

        Algorithm:
        1. Start the monitor.
        2. Set up an object to poll the monitor and for the stop event.
        3. Do forever:
           For each event in the Poll result:
              If it's the stop signal stop.
              If it's an event on the monitor, read devices from the monitor.
                 Use a timeout of 0, because there is an event on the monitor
                 or this code point would not have been reached.
              If it is any other event, raise an error.

        :raises DeviceMonitorError: if an unexpected event found
        """
        self.monitor.start()
        notifier = poll.Poll.for_events(self.monitor, self._stop_event.source)
        while True:
            entries = eintr_retry_call(notifier.poll)
            for file_descriptor, status in entries:
                if file_descriptor == self._stop_event.source.fileno():
                    # in case of a stop event, close our pipe side, and
                    # return from the thread
                    self._stop_event.source.close()
                    return
                elif file_descriptor == self.monitor.fileno():
                    if status is poll.Statuses.READY:
                        read_device = partial(
                           eintr_retry_call,
                           self.monitor.poll,
                           timeout=0
                        )
                        try:
                            for device in iter(read_device, None):
                                self._callback(device)
                        except DeviceMonitorError:
                            raise # FIXME: fixup the monitor
                    else:
                        raise DeviceMonitorError() # FIXME

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
