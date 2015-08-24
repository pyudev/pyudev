# -*- coding: utf-8 -*-
# Copyright (C) 2011, 2012 Sebastian Wiesner <lunaryorn@gmail.com>

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
    pyudev.device._attributes
    =====================

    Handling of device attributes.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@gmail.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
from collections import Mapping

from pyudev._util import ensure_byte_string
from pyudev._util import ensure_unicode_string
from pyudev._util import string_to_bool
from pyudev._util import udev_list_iterate

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
        self._libudev = device._libudev

    def _get_attributes(self):
        """
        Yields attributes of device.
        """
        if hasattr(self._libudev, 'udev_device_get_sysattr_list_entry'):
            attrs = self._libudev.udev_device_get_sysattr_list_entry(
                self.device)
            for attribute, _ in udev_list_iterate(self._libudev, attrs):
                yield ensure_unicode_string(attribute)
        else:
            sys_path = self.device.sys_path
            for filename in os.listdir(sys_path):
                filepath = os.path.join(sys_path, filename)
                if _is_attribute_file(filepath):
                    yield filename

    def __len__(self):
        """
        Return the amount of attributes defined.
        """
        return sum(1 for _ in self._get_attributes())

    def __iter__(self):
        """
        Iterate over all attributes defined.

        Yield each attribute name as unicode string.
        """
        return self._get_attributes()

    def __contains__(self, attribute):
        value = self._libudev.udev_device_get_sysattr_value(
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
        value = self._libudev.udev_device_get_sysattr_value(
            self.device, ensure_byte_string(attribute))
        if value is None:
            raise KeyError(attribute)
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
