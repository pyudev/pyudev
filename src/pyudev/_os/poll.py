# -*- coding: utf-8 -*-
# Copyright (C) 2013 Sebastian Wiesner <lunaryorn@gmail.com>

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
    pyudev._os.poll
    ===============

    Operating system interface for pyudev.

    .. moduleauthor:: Sebastian Wiesner  <lunaryorn@gmail.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import select

from abc import ABCMeta
from six import add_metaclass

from pyudev._util import eintr_retry_call


@add_metaclass(ABCMeta)
class Status(object):
    """
    Status of polled fd.
    """
    # pylint: disable=too-few-public-methods
    pass


class Ready(Status):
    """
    Fd is ready to be read.
    """
    # pylint: disable=too-few-public-methods
    pass
Ready = Ready() # pylint: disable=invalid-name


class HungUp(Status):
    """
    Fd has hung up.
    """
    # pylint: disable=too-few-public-methods
    pass
HungUp = HungUp() # pylint: disable=invalid-name


class NotOpen(Status):
    """
    Fd descriptor is not open.
    """
    # pylint: disable=too-few-public-methods
    pass
NotOpen = NotOpen() # pylint: disable=invalid-name


class Error(Status):
    """
    An error condition of some sort.
    """
    # pylint: disable=too-few-public-methods
    pass
Error = Error() # pylint: disable=invalid-name


class Unknown(Status):
    """
    An unknown status.
    """
    # pylint: disable=too-few-public-methods
    pass
Unknown = Unknown() # pylint: disable=invalid-name


class Statuses(object):
    ERROR = Error
    HUNGUP = HungUp
    NOTOPEN = NotOpen
    READY = Ready
    UNKNOWN = Unknown


class Poll(object):
    """A poll object.

    This object essentially provides a more convenient interface around
    :class:`select.poll`.

    It polls file descriptors exclusively for POLLIN value.
    """

    @staticmethod
    def _has_event(events, event):
        """
        Whether events has event.

        :param int events: a bit vector of events
        :param int event: a single event
        :returns: True if event is among events, otherwise False
        :rtype: bool
        """
        return events & event != 0

    @classmethod
    def for_events(cls, *fds):
        """Listen for POLLIN events on ``fds``.

        :param fds: a list of file descriptors
        :returns: a Poll object set up to recognize the specified events
        :rtype: Poll
        """
        notifier = eintr_retry_call(select.poll)
        for fd in fds:
            notifier.register(fd, select.POLLIN)
        return cls(notifier)

    def __init__(self, notifier):
        """Create a poll object for the given ``notifier``.

        ``notifier`` is the :class:`select.poll` object wrapped by the new poll
        object.

        """
        self._notifier = notifier

    def poll(self, timeout=None):
        """Poll for events.

        ``timeout`` is an integer specifying how long to wait for events (in
        milliseconds).  If omitted, ``None`` or negative, wait until an event
        occurs.

        Return a list of all events that occurred before ``timeout``, where
        each event is a pair ``(fd, event)``. ``fd`` is the integral file
        descriptor, and ``event`` a Status object indicating the event type.

        :rtype: list of tuple of file descriptor * Status
        """
        # Return a list to allow clients to determine whether there are any
        # events at all with a simple truthiness test.
        events = eintr_retry_call(self._notifier.poll, timeout)
        return list(self._parse_events(events))

    def _parse_events(self, events):
        """Parse ``events``.

        ``events`` is a list of events as returned by
        :meth:`select.poll.poll()`.

        Yield all parsed events as tuple of file descriptor and Status

        :raises IOError: on select.POLLNVAL and select.POLLERR

        """
        for fd, event_mask in events:
            status = self._parse_event_mask(event_mask)
            if status is Statuses.NOTOPEN:
                raise IOError('File descriptor not open: {0!r}'.format(fd))
            elif status is Statuses.ERROR:
                raise IOError('Error while polling fd: {0!r}'.format(fd))

            if status in (Statuses.HUNGUP, Statuses.READY):
                yield fd, status

    def _parse_event_mask(self, mask):
        """
        Parse an event mask.

        :param int mask: the mask indicating events
        :returns: the most important aspect of the status
        :rtype: Status
        """
        if self._has_event(mask, select.POLLNVAL):
            return Statuses.NOTOPEN
        elif self._has_event(mask, select.POLLERR):
            return Statuses.ERROR

        if self._has_event(mask, select.POLLIN):
            return Statuses.READY
        if self._has_event(mask, select.POLLHUP):
            return Statuses.HUNGUP

        return Statuses.UNKNOWN
