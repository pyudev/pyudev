# -*- coding: utf-8 -*-
# Copyright (C) 2011 Sebastian Wiesner <lunaryorn@googlemail.com>

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
    pyudev.device
    =============

    Device class implementation of :mod:`pyudev`.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import os
from collections import Mapping
from datetime import timedelta
from itertools import count

from pyudev._libudev import libudev
from pyudev._util import (ensure_byte_string, ensure_unicode_string,
                          udev_list_iterate, string_to_bool)


__all__ = ['Device', 'Attributes',
           'DeviceNotFoundError', 'DeviceNotFoundAtPathError',
           'DeviceNotFoundByNameError', 'DeviceNotFoundInEnvironmentError']


class DeviceNotFoundError(LookupError):
    """
    An error indicating that no :class:`Device` was found.

    .. versionchanged:: 0.5
       Renamed from ``NoSuchDeviceError`` to its current name.
    """


class DeviceNotFoundAtPathError(DeviceNotFoundError):
    """
    A :exc:`DeviceNotFoundError` indicating that no :class:`Device` was
    found at a given path.
    """

    def __init__(self, sys_path):
        DeviceNotFoundError.__init__(self, sys_path)

    @property
    def sys_path(self):
        """
        The path that caused this error as string.
        """
        return self.args[0]

    def __str__(self):
        return 'No device at {0!r}'.format(self.sys_path)


class DeviceNotFoundByNameError(DeviceNotFoundError):
    """
    A :exc:`DeviceNotFoundError` indicating that no :class:`Device` was
    found with a given name.
    """

    def __init__(self, subsystem, sys_name):
        DeviceNotFoundError.__init__(self, subsystem, sys_name)

    @property
    def subsystem(self):
        """
        The subsystem that caused this error as string.
        """
        return self.args[0]

    @property
    def sys_name(self):
        """
        The sys name that caused this error as string.
        """
        return self.args[1]

    def __str__(self):
        return 'No device {0.sys_name!r} in {0.subsystem!r}'.format(self)


class DeviceNotFoundInEnvironmentError(DeviceNotFoundError):
    """
    A :exc:`DeviceNotFoundError` indicating, that no :class:`Device` could
    be constructed from the process environment.
    """

    def __str__(self):
        return 'No device found in environment'


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
       :class:`Device` objects.  :mod:`pyudev` may create multiple
       :class:`Device` objects for the same device.  Instead simply compare
       devices by value using ``==`` or ``!=``.

    :class:`Device` objects are hashable and can therefore be used as keys
    in dictionaries and sets.

    They can also be given directly as ``udev_device *`` to functions wrapped
    through :mod:`ctypes`.
    """

    @classmethod
    def from_path(cls, context, path):
        """
        Create a device from a device ``path``.  The ``path`` may or may not
        start with the ``sysfs`` mount point:

        >>> context = pyudev.Context()
        >>> Device.from_path(context, '/devices/platform')
        Device(u'/sys/devices/platform')
        >>> Device.from_path(context, '/sys/devices/platform')
        Device(u'/sys/devices/platform')

        ``context`` is the :class:`Context` in which to search the device.
        ``path`` is a device path as unicode or byte string.

        Return a :class:`Device` object for the device.  Raise
        :exc:`DeviceNotFoundAtPathError`, if no device was found for ``path``.

        .. versionadded:: 0.4
        """
        if not path.startswith(context.sys_path):
            path = os.path.join(context.sys_path, path.lstrip(os.sep))
        return cls.from_sys_path(context, path)

    @classmethod
    def from_sys_path(cls, context, sys_path):
        """
        Create a new device from a given ``sys_path``:

        >>> context = pyudev.Context()
        >>> Device.from_path(context, '/sys/devices/platform')
        Device(u'/sys/devices/platform')

        ``context`` is the :class:`Context` in which to search the device.
        ``sys_path`` is a unicode or byte string containing the path of the
        device inside ``sysfs`` with the mount point included.

        Return a :class:`Device` object for the device.  Raise
        :exc:`DeviceNotFoundAtPathError`, if no device was found for
        ``sys_path``.

        .. versionchanged:: 0.4
           Raise :exc:`NoSuchDeviceError` instead of returning ``None``, if
           no device was found for ``sys_path``
        .. versionchanged:: 0.5
           Raise :exc:`DeviceNotFoundAtPathError` instead of
           :exc:`NoSuchDeviceError`
        """
        device = libudev.udev_device_new_from_syspath(
            context, ensure_byte_string(sys_path))
        if not device:
            raise DeviceNotFoundAtPathError(sys_path)
        return cls(context, device)

    @classmethod
    def from_name(cls, context, subsystem, sys_name):
        """
        Create a new device from a given ``subsystem`` and a given
        ``sys_name``:

        >>> context = pyudev.Context()
        >>> sda = pyudev.Device.from_name(context, 'block', 'sda')
        >>> sda
        Device(u'/sys/devices/pci0000:00/0000:00:1f.2/host0/target0:0:0/0:0:0:0/block/sda')
        >>> sda == pyudev.Device.from_path(context, '/block/sda')

        ``context`` is the :class:`Context` in which to search the device.
        ``subsystem`` and ``sys_name`` are byte or unicode strings, which
        denote the subsystem and the name of the device to create.

        Return a :class:`Device` object for the device.  Raise
        :exc:`DeviceNotFoundByNameError`, if no device was found with the given
        name.

        .. versionadded:: 0.5
        """
        device = libudev.udev_device_new_from_subsystem_sysname(
            context, ensure_byte_string(subsystem),
            ensure_byte_string(sys_name))
        if not device:
            raise DeviceNotFoundByNameError(subsystem, sys_name)
        return cls(context, device)

    @classmethod
    def from_environment(cls, context):
        """
        Create a new device from the process environment (as in
        :data:`os.environ`).

        This only works reliable, if the current process is called from an
        udev rule, and is usually used for tools executed from ``IMPORT=``
        rules.  Use this method to create device objects in Python scripts
        called from udev rules.

        ``context`` is the library :class:`Context`.

        Return a :class:`Device` object constructed from the environment.
        Raise :exc:`DeviceNotFoundInEnvironmentError`, if no device could be
        created from the environment.

        .. versionadded:: 0.6

        .. udevminversion:: 152
        """
        device = libudev.udev_device_new_from_environment(context)
        if not device:
            raise DeviceNotFoundInEnvironmentError()
        return cls(context, device)

    def __init__(self, context, _device):
        self.context = context
        self._as_parameter_ = _device
        self._attributes = Attributes(self)

    def __del__(self):
        libudev.udev_device_unref(self)

    def __repr__(self):
        return 'Device({0.sys_path!r})'.format(self)

    @property
    def parent(self):
        """
        The parent :class:`Device` or ``None``, if there is no parent
        device.
        """
        parent = libudev.udev_device_get_parent(self)
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

    def find_parent(self, subsystem, device_type=None):
        """
        Find the parent device with the given ``subsystem`` and
        ``device_type``.

        ``subsystem`` is a byte or unicode string containing the name of the
        subsystem, in which to search for the parent.  ``device_type`` is a
        byte or unicode string holding the expected device type of the parent.
        It can be ``None`` (the default), which means, that no specific device
        type is expected.

        Return a parent :class:`Device` within the given ``subsystem`` and – if
        ``device_type`` is not ``None`` – with the given ``device_type``, or
        ``None``, if this device has no parent device matching these
        constraints.

        .. versionadded:: 0.9
        """
        subsystem = ensure_byte_string(subsystem)
        if device_type is not None:
            device_type = ensure_byte_string(device_type)
        parent = libudev.udev_device_get_parent_with_subsystem_devtype(
            self, subsystem, device_type)
        if not parent:
            return None
        # parent device is not referenced, thus forcibly acquire a reference
        return Device(self.context, libudev.udev_device_ref(parent))

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
        Absolute path of this device in ``sysfs`` including the ``sysfs``
        mount point as unicode string.
        """
        return ensure_unicode_string(libudev.udev_device_get_syspath(self))

    @property
    def device_path(self):
        """
        Kernel device path as unicode string.  This path uniquely identifies
        a single device.

        Unlike :attr:`sys_path`, this path does not contain the ``sysfs``
        mount point.  However, the path is absolute and starts with a slash
        ``'/'``.
        """
        return ensure_unicode_string(libudev.udev_device_get_devpath(self))

    @property
    def subsystem(self):
        """
        Name of the subsystem this device is part of as unicode string.
        """
        return ensure_unicode_string(libudev.udev_device_get_subsystem(self))

    @property
    def sys_name(self):
        """
        Device file name inside ``sysfs`` as unicode string.
        """
        return ensure_unicode_string(libudev.udev_device_get_sysname(self))

    @property
    def device_type(self):
        """
        Device type as unicode string, or ``None``, if the device type is
        unknown.

        >>> context = Context()
        >>> for device in context.list_devices(subsystem='net'):
        ...     '{0} - {1}'.format(device.sys_name, device.device_type or 'ethernet')
        ...
        u'eth0 - ethernet'
        u'wlan0 - wlan'
        u'lo - ethernet'
        u'vboxnet0 - ethernet'
        """
        device_type = libudev.udev_device_get_devtype(self)
        if device_type is not None:
            return ensure_unicode_string(device_type)

    @property
    def driver(self):
        """
        The driver name as unicode string, or ``None``, if there is no
        driver for this device.

        .. versionadded:: 0.5
        """
        driver = libudev.udev_device_get_driver(self)
        if driver:
            return ensure_unicode_string(driver)

    @property
    def device_node(self):
        """
        Absolute path to the device node of this device as unicode string or
        ``None``, if this device doesn't have a device node.  The path
        includes the device directory (see :attr:`Context.device_path`).

        This path always points to the actual device node associated with
        this device, and never to any symbolic links to this device node.
        See :attr:`device_links` to get a list of symbolic links to this
        device node.
        """
        node = libudev.udev_device_get_devnode(self)
        if node:
            return ensure_unicode_string(node)

    @property
    def is_initialized(self):
        """
        ``True``, if the device is initialized, ``False`` otherwise.

        A device is initialized, if udev has already handled this device and
        has set up device node permissions and context, or renamed a network
        device.

        Consequently, this property is only implemented for devices with a
        device node or for network devices.  On all other devices this property
        is always ``True``.

        It is *not* recommended, that you use uninitialized devices.

        .. seealso:: :attr:`time_since_initialized`

        .. versionadded:: 0.8

        .. udevminversion:: 165
        """
        return bool(libudev.udev_device_get_is_initialized(self))

    @property
    def time_since_initialized(self):
        """
        The time elapsed since initialization as :class:`~datetime.timedelta`.

        This property is only implemented on devices, which need to store
        properties in the udev database.  On all other devices this property is
        simply zero :class:`~datetime.timedelta`.

        .. seealso:: :attr:`is_initialized`

        .. versionadded:: 0.8

        .. udevminversion:: 165
        """
        microseconds = libudev.udev_device_get_usec_since_initialized(self)
        return timedelta(microseconds=microseconds)

    @property
    def device_links(self):
        """
        An iterator, which yields the absolute paths (including the device
        directory, see :attr:`Context.device_path`) of all symbolic links
        pointing to the :attr:`device_node` of this device.  The paths are
        unicode strings.

        UDev can create symlinks to the original device node (see
        :attr:`device_node`) inside the device directory.  This is often
        used to assign a constant, fixed device node to devices like
        removeable media, which technically do not have a constant device
        node, or to map a single device into multiple device hierarchies.
        The property provides access to all such symbolic links, which were
        created by UDev for this device.
        """
        entry = libudev.udev_device_get_devlinks_list_entry(self)
        for name in udev_list_iterate(entry):
            yield ensure_unicode_string(name)

    @property
    def attributes(self):
        """
        The system attributes of this device as read-only
        :class:`Attributes` mapping.

        System attributes are basically normal files inside the the device
        directory.  These files contain all sorts of information about the
        device, which may not be reflected by properties.  These attributes
        are commonly used for matching in udev rules, and can be printed
        using ``udevadm info --attribute-walk``.

        The values of these attributes are not always proper strings, and
        can contain arbitrary bytes.

        .. versionadded:: 0.5
        """
        return self._attributes

    @property
    def tags(self):
        """
        An iterator, which yields all attached tags as unicode strings.

        .. versionadded:: 0.6

        .. udevminversion:: 154
        """
        entry = libudev.udev_device_get_tags_list_entry(self)
        for tag in udev_list_iterate(entry):
            yield ensure_unicode_string(tag)

    def __iter__(self):
        """
        Iterate over the names of all properties defined for this device.

        Return a generator yielding the names of all properties of this
        device as unicode strings.
        """
        entry = libudev.udev_device_get_properties_list_entry(self)
        for name in udev_list_iterate(entry):
            yield ensure_unicode_string(name)

    def __len__(self):
        """
        Return the amount of properties defined for this device as integer.
        """
        entry = libudev.udev_device_get_properties_list_entry(self)
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
            self, ensure_byte_string(property))
        if value is None:
            raise KeyError('No such property: {0}'.format(property))
        return ensure_unicode_string(value)

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

        A boolean property has either a value of ``'1'`` or of ``'0'``,
        where ``'1'`` stands for ``True``, and ``'0'`` for ``False``.  Any
        other value causes a :exc:`~exceptions.ValueError` to be raised.

        ``property`` is a unicode or byte string containing the name of the
        property.

        Return ``True``, if the property value is ``'1'`` and ``False``, if
        the property value is ``'0'``.  Any other value raises a
        :exc:`~exceptions.ValueError`.  Raise a :exc:`~exceptions.KeyError`,
        if the given property is not defined for this device.
        """
        return string_to_bool(self[property])

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


def _is_attribute_file(filepath):
    """
    Check, if ``filepath`` points to a valid udev attribute filename.

    Implementation is stolen from udev source code, ``print_all_attributes``
    in ``udev/udevadm-info.c``.  It excludes hidden files (starting with a
    dot), the special files ``dev`` and ``uevent`` and links.

    Return ``True``, if ``filepath`` refers to an attribute, ``False``
    otherwise.
    """
    filename = os.path.basename(filepath)
    return not (filename.startswith('.') or
                filename in ('dev', 'uevent') or
                os.path.islink(filepath))


class Attributes(Mapping):
    """
    A mapping which holds udev attributes for :class:`Device` objects.

    This class subclasses the ``Mapping`` ABC, providing a read-only
    dictionary mapping attribute names to the corresponding values.
    Therefore all well-known dicitionary methods and operators
    (e.g. ``.keys()``, ``.items()``, ``in``) are available to access device
    attributes.

    .. versionadded:: 0.5
    """

    def __init__(self, device):
        self.device = device

    @property
    def _attribute_files(self):
        sys_path = self.device.sys_path
        return [fn for fn in os.listdir(sys_path) if
                _is_attribute_file(os.path.join(sys_path, fn)) and
                fn in self]

    def __len__(self):
        """
        Return the amount of attributes defined.
        """
        return len(self._attribute_files)

    def __iter__(self):
        """
        Iterate over all attributes defined.

        Yield each attribute name as unicode string.
        """
        return iter(self._attribute_files)

    def __contains__(self, attribute):
        value = libudev.udev_device_get_sysattr_value(
            self.device, ensure_byte_string(attribute))
        return value is not None

    def __getitem__(self, attribute):
        """
        Get the given system ``attribute`` for the device.

        ``attribute`` is a unicode or byte string containing the name of the
        system attribute.

        Return the attribute value as byte string, or raise a
        :exc:`~exceptions.KeyError`, if the given attribute is not defined
        for this device.
        """
        value = libudev.udev_device_get_sysattr_value(
            self.device, ensure_byte_string(attribute))
        if value is None:
            raise KeyError('No such attribute: {0}'.format(attribute))
        return value

    def asstring(self, attribute):
        """
        Get the given ``atribute`` for the device as unicode string.

        Depending on the content of the attribute, this may or may not work.
        Be prepared to catch :exc:`~exceptions.UnicodeDecodeError`.

        ``attribute`` is a unicode or byte string containing the name of the
        attribute.

        Return the attribute value as byte string.  Raise a
        :exc:`~exceptions.KeyError`, if the given attribute is not defined
        for this device, or :exc:`~exceptions.UnicodeDecodeError`, if the
        content of the attribute cannot be decoded into a unicode string.
        """
        return ensure_unicode_string(self[attribute])

    def asint(self, attribute):
        """
        Get the given ``attribute`` as integer.

        ``attribute`` is a unicode or byte string containing the name of the
        attribute.

        Return the attribute value as integer. Raise a
        :exc:`~exceptions.KeyError`, if the given attribute is not defined
        for this device, or a :exc:`~exceptions.ValueError`, if the
        attribute value cannot be converted to an integer.
        """
        return int(self.asstring(attribute))

    def asbool(self, attribute):
        """
        Get the given ``attribute`` from this device as boolean.

        A boolean attribute has either a value of ``'1'`` or of ``'0'``,
        where ``'1'`` stands for ``True``, and ``'0'`` for ``False``.  Any
        other value causes a :exc:`~exceptions.ValueError` to be raised.

        ``attribute`` is a unicode or byte string containing the name of the
        attribute.

        Return ``True``, if the attribute value is ``'1'`` and ``False``, if
        the attribute value is ``'0'``.  Any other value raises a
        :exc:`~exceptions.ValueError`.  Raise a :exc:`~exceptions.KeyError`,
        if the given attribute is not defined for this device.
        """
        return string_to_bool(self.asstring(attribute))
