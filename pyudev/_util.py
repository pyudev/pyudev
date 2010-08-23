# -*- coding: utf-8 -*-
# Copyright (c) 2010 Sebastian Wiesner <lunaryorn@googlemail.com>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.


import os
import sys
from errno import ENOMEM

from pyudev._libudev import libudev


def assert_bytes(value):
    if not isinstance(value, str):
        value = value.encode(sys.getfilesystemencoding())
    return value

def property_value_to_bytes(value):
    if isinstance(value, str):
        return value
    elif isinstance(value, unicode):
        return value.encode(sys.getfilesystemencoding())
    elif isinstance(value, int):
        return str(int(value))
    else:
        return str(value)

def udev_list_iterate(entry):
    while entry:
        yield libudev.udev_list_entry_get_name(entry)
        entry = libudev.udev_list_entry_get_next(entry)

def call_handle_error_return(func, *args):
    """
    Call ``func`` with ``args``, and handle the return code.  If the return
    code is non-null, it is interpreted as negative :mod:`errno` code.  In
    case of :attr:`errno.ENOMEM`, :exc:`MemoryError` is raised, otherwise an
    :exc:`EnvironmentError` with proper ``errno`` and ``strerror``
    attributes is raised.
    """
    errorcode = func(*args)
    if errorcode != 0:
        # udev returns the *negative* errno code at this point
        errno = -errorcode
        if errno == ENOMEM:
            raise MemoryError()
        else:
            raise EnvironmentError(errno, os.strerror(errno))
