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


import os
import sys
from errno import ENOMEM

from pyudev._libudev import libudev


def assert_bytes(value):
    if not isinstance(value, bytes):
        value = value.encode(sys.getfilesystemencoding())
    return value

def assert_unicode(value):
    if not isinstance(value, unicode):
        value = value.decode(sys.getfilesystemencoding())
    return value


def property_value_to_bytes(value):
    # udev represents boolean values as 1 or 0, therefore an explicit
    # conversion to int is required for boolean values
    if isinstance(value, bool):
        value = int(value)
    if isinstance(value, bytes):
        return value
    else:
        return unicode(value).encode(sys.getfilesystemencoding())

def string_to_bool(value):
    if value not in ('1', '0'):
        raise ValueError('Not a boolean value: {0!r}'.format(value))
    return value == '1'

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
