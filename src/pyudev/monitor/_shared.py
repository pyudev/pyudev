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
    pyudev.monitor._shared
    ======================

    Shared methods for monitor.

    .. moduleauthor::  Anne Mulhern  <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from pyudev._errors import DeviceValueError

from pyudev._os import poll


def poll_err_str(fd, status):
    """
    Gives an error message for the status.

    :param Status status: status of polling object
    :return: an error message
    :rtype: str
    """
    if status is poll.Statuses.ERROR:
        return 'File descriptor not open: {0!r}'.format(fd)
    if status is poll.Statuses.NOTOPEN:
        return 'File descriptor not open: {0!r}'.format(fd)
    if status is poll.Statuses.UNKNOWN:
        return 'Unknown status for file descriptor: {0!r}'.format(fd)
    if status is poll.Statuses.HUNGUP:
        return 'File descriptor hung up: {0!r}'.format(fd)
    raise DeviceValueError(status, "status")
