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

from pyudev._util import eintr_retry_call


class Poll(object):
    """A poll object.

    This object essentially provides a more convenient interface around
    :class:`select.poll`.

    It polls file descriptors exclusively for POLLIN value.
    """

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
        descriptor, and ``event`` a bitmask indicating the event type.
        """
        return eintr_retry_call(self._notifier.poll, timeout)
