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

    The central class is the :class:`Context`.  To use this library, create
    an instance of this class first.  Then use this class to list devices.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""


import sys
from collections import Mapping

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
        """
        Return an :class:`Enumerator` to list devices.
        """
        return Enumerator(self)


def _assert_bytes(value):
    if not isinstance(value, str):
        value = value.encode(sys.getfilesystemencoding())
    return value

def _property_value_to_bytes(value):
    if isinstance(value, str):
        return value
    elif isinstance(value, unicode):
        return value.encode(sys.getfilesystemencoding())
    elif isinstance(value, int):
        return str(int(value))
    else:
        return str(value)

def _property_value_from_bytes(value):
    if value.isdigit():
        return int(value)
    else:
        return value.decode(sys.getfilesystemencoding())

def _udev_list_iterate(entry):
    while entry:
        yield libudev.udev_list_entry_get_name(entry)
        entry = libudev.udev_list_entry_get_next(entry)

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
    >>> for device in devices:
    ...     device.sys_name
    ...
    u'event7'
    u'mouse2'
    u'event4'
    u'mouse0'
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
        for name in _udev_list_iterate(entry):
            yield Device.from_sys_path(self.context, name)


class Device(Mapping):
    """
    A single device.

    This class subclasses the ``Mapping`` ABC, devices therefore support the
    dictionary protocol.  They map sysfs properties to the corresponding
    values:

    >>> context = Context
    >>> devices = context.list_devices().match_subsystem('input')
    >>> for device in devices:
    ...     if device.sys_name.startswith('event'):
    ...         device.sys_name, device.get('ID_INPUT_MOUSE')
    ...
    (u'event6', None)
    (u'event7', 1)
    (u'event3', None)
    (u'event4', 1)
    (u'event5', None)
    """

    @classmethod
    def from_sys_path(cls, context, sys_path):
        """
        Create a device from the given :class:`Context` and the given
        ``sys_path``.
        """
        if not isinstance(context, Context):
            raise TypeError('Invalid context object')
        device = libudev.udev_device_new_from_syspath(
            context._context, _assert_bytes(sys_path))
        return cls(context, device)

    def __init__(self, context, _device):
        self.context = context
        self._device = _device

    def __repr__(self):
        return 'Device({0.sys_path!r})'.format(self)

    @property
    def sys_path(self):
        """
        Absolute path of this device in ``sysfs`` including the mount point.
        """
        return libudev.udev_device_get_syspath(self._device).decode(
            sys.getfilesystemencoding())

    @property
    def dev_path(self):
        """
        Kernel device path.

        Unlike :attr:`sys_path`, this path does not contain the mount point.
        However, the path is absolute and starts with a slash ``'/'``.
        """
        return libudev.udev_device_get_devpath(self._device).decode(
            sys.getfilesystemencoding())

    @property
    def subsystem(self):
        """
        Name of the subsystem, this device is part of.
        """
        return libudev.udev_device_get_subsystem(self._device).decode(
            sys.getfilesystemencoding())

    @property
    def sys_name(self):
        """
        Device name inside ``sysfs``.
        """
        return libudev.udev_device_get_sysname(self._device).decode(
            sys.getfilesystemencoding())

    @property
    def dev_node(self):
        """
        Absolute path to the device node (including the device directory).
        """
        return libudev.udev_device_get_devnode(self._device).decode(
            sys.getfilesystemencoding())

    @property
    def devlinks(self):
        """
        Return all device file links in the device directory, which point to
        this device.
        """
        entry = libudev.udev_device_get_devlinks_list_entry(self._device)
        for name in _udev_list_iterate(entry):
            yield name.decode(sys.getfilesystemencoding())

    def __iter__(self):
        entry = libudev.udev_device_get_properties_list_entry(self._device)
        for name in _udev_list_iterate(entry):
            yield name.decode(sys.getfilesystemencoding())

    def __len__(self):
        return len(list(self))

    def __getitem__(self, property):
        """
        Get a property from this device.
        """
        value = libudev.udev_device_get_property_value(
            self._device, _assert_bytes(property))
        if value is None:
            raise KeyError('No such property: {0}'.format(property))
        return _property_value_from_bytes(value)

    def __eq__(self, other):
        return self.dev_path == other.dev_path

    def __ne__(self, other):
        return self.dev_path != other.dev_path
