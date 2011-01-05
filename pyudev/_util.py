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
    pyudev._util
    ============

    Internal utilities

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""


from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import sys

from pyudev._libudev import libudev


def assert_bytes(value):
    """
    Return the given ``value`` as bytestring.

    If the given ``value`` is not a byte string, but a real unicode string, it
    is encoded with the filesystem encoding (as in
    :func:`sys.getfilesystemencoding()`).
    """
    if not isinstance(value, bytes):
        value = value.encode(sys.getfilesystemencoding())
    return value


def assert_unicode(value):
    """
    Return the given ``value`` as unicode string.

    If the given ``value`` is not a unicode string, but a byte string, it is
    decoded with the filesystem encoding (as in
    :func:`sys.getfilesystemencoding()`).
    """
    if not isinstance(value, unicode):
        value = value.decode(sys.getfilesystemencoding())
    return value


def property_value_to_bytes(value):
    """
    Return a byte string, which represents the given ``value`` in a way
    suitable as raw value of an udev property.

    If ``value`` is a boolean object, it is converted to ``'1'`` or ``'0'``,
    depending on whether ``value`` is ``True`` or ``False``.  If ``value`` is a
    byte string already, it is returned unchanged.  Anything else is simply
    converted to a unicode string, and then passed to :func:`assert_bytes`.
    """
    # udev represents boolean values as 1 or 0, therefore an explicit
    # conversion to int is required for boolean values
    if isinstance(value, bool):
        value = int(value)
    if isinstance(value, bytes):
        return value
    else:
        return assert_bytes(unicode(value))


def string_to_bool(value):
    """
    Convert the given unicode string ``value`` to a boolean object.

    If ``value`` is ``'1'``, ``True`` is returned.  If ``value`` is ``'0'``,
    ``False`` is returned.  Any other value raises a
    :exc:`~exceptions.ValueError`.
    """
    if value not in ('1', '0'):
        raise ValueError('Not a boolean value: {0!r}'.format(value))
    return value == '1'


def udev_list_iterate(entry):
    """
    Iteration helper for udev list entry objects.

    Simply yield all next entries starting with ``entry``, until there is no
    next entry anymore.
    """
    while entry:
        yield libudev.udev_list_entry_get_name(entry)
        entry = libudev.udev_list_entry_get_next(entry)
