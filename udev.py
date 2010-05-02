# Copyright (C) 2010 Sebastian Wiesner <lunaryorn@googlemail.com>

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
    udev
    ====

    A binding to ``libudev``.

    To use this library, a :class:`Context` is required:

    >>> context = Context()

    This contains provides an interface to all udev operations.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""


import sys

import _udev

libudev = _udev.load_udev_library()


class Context(object):
    """
    The udev context.

    The context is the central object to access udev.  It represents the
    udev configuration and is required for all udev operations.

    The context is iterable, and returns a :class:`Enumerator` upon
    iteration.  This enumerator provides miscellaneous methods to filter the
    device tree.
    """

    def __init__(self):
        self._context = libudev.udev_new()

    def __del__(self):
        libudev.udev_unref(self._context)

    @property
    def sys_path(self):
        """
        The ``sysfs`` mount point as string, defaults to ``/sys'``.

        You can override the mount point using the environment variable
        :envvar:`SYSFS_PATH`.
        """
        return libudev.udev_get_sys_path(self._context).decode(
            sys.getfilesystemencoding())

    @property
    def dev_path(self):
        """
        The device directory path as string, defaults to ``/dev``.

        The actual value can be overridden in the udev configuration.
        """
        return libudev.udev_get_dev_path(self._context).decode(
            sys.getfilesystemencoding())

    def list_devices(self):
        return Enumerator(self)


def _assert_bytes(v):
    if not isinstance(v, str):
        v = v.encode(sys.getfilesystemencoding())
    return v

def _property_value_to_bytes(v):
    if isinstance(v, str):
        return v
    elif isinstance(v, unicode):
        return v.encode(sys.getfilesystemencoding())
    elif isinstance(v, int):
        return str(int(v))
    else:
        return str(v)

def _check_call(func, *args):
    res = func(*args)
    if res != 0:
        raise EnvironmentError(
            '{0.__name__} returned error code {1}'.format(func, res))
    return res


class Enumerator(object):
    """
    An iterable over the list of devices.

    >>> context = Context()
    >>> devices = context.list_devices()

    Before iterating, the list can be filtered by different criteria:

    >>> devices = devices.match_subsystem('input').match_property(
    ...     'ID_INPUT_MOUSE', True)
    """

    def __init__(self, context):
        """
        Create a new enumerator with the given ``context`` (a
        :class:`Context` instance).

        While you can create objects of this class directly, this is not
        recommended.  You should call :func:`iter` on the ``context`` to
        retrieve an enumerator.
        """
        if not isinstance(context, Context):
            raise TypeError('Invalid context object')
        self.context = context
        self._enumerator = libudev.udev_enumerate_new(context._context)

    def __del__(self):
        libudev.udev_enumerate_unref(self._enumerator)

    def match_subsystem(self, subsystem):
        """
        Include all devices, which are part of the given ``subsystem``.
        """
        _check_call(libudev.udev_enumerate_add_match_subsystem,
                    self._enumerator, _assert_bytes(subsystem))
        return self

    def match_property(self, property, value):
        """
        Include all devices, whose ``property`` has the given ``value``.
        """
        _check_call(libudev.udev_enumerate_add_match_property,
                    self._enumerator, _assert_bytes(property),
                    _property_value_to_bytes(value))
        return self

    def __iter__(self):
        _check_call(libudev.udev_enumerate_scan_devices, self._enumerator)
        entry = libudev.udev_enumerate_get_list_entry(self._enumerator)
        while entry:
            yield libudev.udev_list_entry_get_name(entry)
            entry = libudev.udev_list_entry_get_next(entry)

