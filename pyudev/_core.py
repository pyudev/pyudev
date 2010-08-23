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


from __future__ import absolute_import

import sys
from itertools import count
from collections import Mapping

from pyudev._libudev import libudev
from pyudev._util import (assert_bytes, property_value_to_bytes,
                          call_handle_error_return, udev_list_iterate)


class Context(object):
    """
    The udev context.

    This is *the* central object to access udev.  An instance of this class
    must be created before anything else can be done.  It holds the udev
    configuration and provides the interface to list devices (see
    :meth:`list_devices`).
    """

    def __init__(self):
        """
        Create a new context.
        """
        self._context = libudev.udev_new()

    def __del__(self):
        libudev.udev_unref(self._context)

    @property
    def sys_path(self):
        """
        The ``sysfs`` mount point defaulting to ``/sys'`` as unicode string.

        The mount point can be overwritten using the environment variable
        :envvar:`SYSFS_PATH`.  Use this for testing purposes.
        """
        return libudev.udev_get_sys_path(self._context).decode(
            sys.getfilesystemencoding())

    @property
    def device_path(self):
        """
        The device directory path defaulting to ``/dev`` as unicode string.

        This can be overridden in the udev configuration.
        """
        return libudev.udev_get_dev_path(self._context).decode(
            sys.getfilesystemencoding())

    def list_devices(self):
        """
        List all available devices.

        This function creates and returns an :class:`Enumerator` object,
        that can be used to filter the list of devices, and eventually
        retrieve :class:`Device` objects representing matching devices.
        """
        return Enumerator(self)


class Enumerator(object):
    """
    Enumerate all available devices.

    To retrieve devices, simply iterate over an instance of this class.
    This operation yields :class:`Device` objects representing the available
    devices.

    Before iteration the device list can be filtered by subsystem or by
    property values using :meth:`match_subsystem` and
    :meth:`match_property`.  Multiple subsystem (property) filters are
    combined using a logical OR, filters of different types are combined
    using a logical AND.  The following filter for instance::

        devices.match_subsystem('block').match_property(
            'ID_TYPE', 'disk').match_property('DEVTYPE', 'disk')

    means the following::

        subsystem == 'block' and (ID_TYPE == 'disk' or DEVTYPE == 'disk')

    Once added, a filter cannot be removed anymore.  Create a new object
    instead.
    """

    def __init__(self, context):
        """
        Create a new enumerator with the given ``context`` (a
        :class:`Context` instance).

        While you can create objects of this class directly, this is not
        recommended.  Call :method:`Context.list_devices()` instead.
        """
        if not isinstance(context, Context):
            raise TypeError('Invalid context object')
        self.context = context
        self._enumerator = libudev.udev_enumerate_new(context._context)
        self._parents = []

    def __del__(self):
        libudev.udev_enumerate_unref(self._enumerator)

    def match_subsystem(self, subsystem):
        """
        Include all devices, which are part of the given ``subsystem``.

        ``subsystem`` is either a unicode string or a byte string,
        containing the name of the subsystem.

        Return the instance again.
        """
        call_handle_error_return(
            libudev.udev_enumerate_add_match_subsystem,
            self._enumerator, assert_bytes(subsystem))
        return self

    def match_property(self, property, value):
        """
        Include all devices, whose ``property`` has the given ``value``.

        ``property`` is either a unicode string or a byte string, containing
        the name of the property to match.  ``value`` is a property value,
        being one of the following types:

        - :func:`int`
        - :func:`bool`
        - A unicode or byte string
        - Anything convertable to a byte string

        Return the instance again.
        """
        call_handle_error_return(
            libudev.udev_enumerate_add_match_property,
            self._enumerator, assert_bytes(property),
            property_value_to_bytes(value))
        return self

    def match_children(self, device):
        """
        Include all *direct* children of the given ``device``.  A child is a
        device, whose :attr:`Device.parent` points to ``device``.

        Return the instance again.
        """
        self._parents.append(device)
        return self

    def __iter__(self):
        """
        Iterate over all matching devices.

        Yield :class:`Device` objects.
        """
        call_handle_error_return(
            libudev.udev_enumerate_scan_devices, self._enumerator)
        entry = libudev.udev_enumerate_get_list_entry(self._enumerator)
        for name in udev_list_iterate(entry):
            device = Device.from_sys_path(self.context, name)
            if (not self._parents) or any(device.parent == p for p
                                          in self._parents):
                yield device


class NoSuchDeviceError(LookupError):
    """
    An error indicating that no :class:`Device` was found for a specific
    path.
    """

    def __init__(self, sys_path):
        LookupError.__init__(self, sys_path)

    @property
    def sys_path(self):
        """The path that caused this error"""
        return self.args[0]

    def __str__(self):
        return 'No such device: {0!r}'.format(self.sys_path)


class Device(Mapping):
    """
    A single device with attached attributes and properties.

    This class subclasses the ``Mapping`` ABC, providing a read-only
    dictionary mapping property names to the corresponding values.
    Therefore all well-known dicitionary methods and operators
    (e.g. ``.keys()``, ``.items()``, ``in``) are available to access device
    properties.

    Aside of the properties, a device also has a set of udev-specific
    attributes like the path inside ``sysfs``.

    :class:`Device` objects compare equal and unequal to other devices and
    to strings (based on :attr:`device_path`).  However, there is no
    ordering on :class:`Device` objects, and the corresponding operators
    ``>``, ``<``, ``<=`` and ``>=`` raise :exc:`~exceptions.TypeError`.

    .. warning::

       Do **never** use object identity (``is`` operator) to compare
       :class:`Device` objects.  :mod:`udev` may create multiple
       :class:`Device` objects for the same device.  Instead simply compare
       devices by value using ``==`` or ``!=``.

    :class:`Device` objects are hashable and can therefore be used as keys
    in dictionaries and sets.
    """

    @classmethod
    def from_sys_path(cls, context, sys_path):
        """
        Create a new device from a given ``sys_path``:

        >>> context = Context()
        >>> Device.from_path(context, '/sys/devices/platform')
        Device(u'/sys/devices/platform')

        ``context`` is the :class:`Context` in which to search the device.
        ``sys_path`` is a unicode or byte string containing the path of the
        device inside ``sysfs`` with the mount point included.

        Return a :class:`Device` object for the device.  Raise
        :exc:`NoSuchDeviceError`, if no device was found for ``sys_path``.

        .. versionchanged:: 0.4
           Raise :exc:`NoSuchDeviceError` instead of returning ``None``, if
           no device was found for ``sys_path``
        """
        if not isinstance(context, Context):
            raise TypeError('Invalid context object')
        device = libudev.udev_device_new_from_syspath(
            context._context, assert_bytes(sys_path))
        if not device:
            raise NoSuchDeviceError(sys_path)
        return cls(context, device)

    def __init__(self, context, _device):
        self.context = context
        self._device = _device

    def __del__(self):
        libudev.udev_device_unref(self._device)

    def __repr__(self):
        return 'Device({0.sys_path!r})'.format(self)

    @property
    def parent(self):
        """
        The parent :class:`Device` or ``None``, if there is no parent
        device.
        """
        parent = libudev.udev_device_get_parent(self._device)
        if not parent:
            return None
        # the parent device is not referenced, thus forcibly acquire a
        # reference
        return Device(self.context, libudev.udev_device_ref(parent))

    @property
    def children(self):
        """
        Yield all direct children of this device.

        .. note::

           As the underlying library does not provide any means to directly
           query the children of a device, this property performs a linear
           search through all devices.

        Return an iterable yielding a :class:`Device` object for each direct
        child of this device.
        """
        for device in self.context.list_devices().match_children(self):
            yield device

    def traverse(self):
        """
        Traverse all parent devices of this device from bottom to top.

        Return an iterable yielding all parent devices as :class:`Device`
        objects, *not* including the current device.  The last yielded
        :class:`Device` is the top of the device hierarchy.
        """
        parent = self.parent
        while parent:
            yield parent
            parent = parent.parent

    @property
    def sys_path(self):
        """
        Absolute path of this device in ``sysfs`` including the mount point
        as unicode string.
        """
        return libudev.udev_device_get_syspath(self._device).decode(
            sys.getfilesystemencoding())

    @property
    def device_path(self):
        """
        Kernel device path as unicode string.  This path uniquely identifies
        a single device.

        Unlike :attr:`sys_path`, this path does not contain the mount point.
        However, the path is absolute and starts with a slash ``'/'``.
        """
        return libudev.udev_device_get_devpath(self._device).decode(
            sys.getfilesystemencoding())

    @property
    def subsystem(self):
        """
        Name of the subsystem this device is part of as unicode string.
        """
        return libudev.udev_device_get_subsystem(self._device).decode(
            sys.getfilesystemencoding())

    @property
    def sys_name(self):
        """
        Device file name inside ``sysfs`` as unicode string.
        """
        return libudev.udev_device_get_sysname(self._device).decode(
            sys.getfilesystemencoding())

    @property
    def device_node(self):
        """
        Absolute path to the device node inside the device directory
        (including the device directory) as unicode string.
        """
        return libudev.udev_device_get_devnode(self._device).decode(
            sys.getfilesystemencoding())

    @property
    def device_links(self):
        """
        The device file links in the device directory, which point to this
        device as a list of unicode strings.
        """
        entry = libudev.udev_device_get_devlinks_list_entry(self._device)
        for name in udev_list_iterate(entry):
            yield name.decode(sys.getfilesystemencoding())

    def __iter__(self):
        """
        Iterate over the names of all properties defined for this device.
        Property names are unicode strings.
        """
        entry = libudev.udev_device_get_properties_list_entry(self._device)
        for name in udev_list_iterate(entry):
            yield name.decode(sys.getfilesystemencoding())

    def __len__(self):
        """
        Return the amount of properties defined for this device.
        """
        entry = libudev.udev_device_get_properties_list_entry(self._device)
        counter = count()
        for _ in udev_list_iterate(entry):
            next(counter)
        return next(counter)

    def __getitem__(self, property):
        """
        Get the given ``property`` from this device.

        ``property`` is a unicode or byte string containing the name of the
        property.

        Return the property value as unicode string, or raise a
        :exc:`~exceptions.KeyError`, if the given property is not defined
        for this device.
        """
        value = libudev.udev_device_get_property_value(
            self._device, assert_bytes(property))
        if value is None:
            raise KeyError('No such property: {0}'.format(property))
        return value.decode(sys.getfilesystemencoding())

    def asint(self, property):
        """
        Get the given ``property`` from this device as integer.

        ``property`` is a unicode or byte string containing the name of the
        property.

        Return the property value as integer. Raise a
        :exc:`~exceptions.KeyError`, if the given property is not defined
        for this device, or a :exc:`~exceptions.ValueError`, if the property
        value cannot be converted to an integer.
        """
        return int(self[property])

    def asbool(self, property):
        """
        Get the given ``property`` from this device as boolean.

        ``property`` is a unicode or byte string containing the name of the
        property.

        Return the property value as boolean.  A property value of ``'1'``
        is considered ``True``, a property value of ``'0'`` is considered
        ``False``, any other property value raises a
        :exc:`~exceptions.ValueError`.  Raise a
        :exc:`~exceptions.ValueError`, if the property value cannot be
        converted to an integer.
        """
        value = self[property]
        if value not in ('1', '0'):
            raise ValueError('Invalid value for boolean property: '
                             '{0!r}'.format(value))
        return value == '1'

    def __hash__(self):
        return hash(self.device_path)

    def __eq__(self, other):
        if isinstance(other, Device):
            return self.device_path == other.device_path
        else:
            return self.device_path == other

    def __ne__(self, other):
        if isinstance(other, Device):
            return self.device_path != other.device_path
        else:
            return self.device_path != other

    def __gt__(self, other):
        raise TypeError('Device not orderable')

    def __lt__(self, other):
        raise TypeError('Device not orderable')

    def __le__(self, other):
        raise TypeError('Device not orderable')

    def __ge__(self, other):
        raise TypeError('Device not orderable')
