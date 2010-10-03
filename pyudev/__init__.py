# -*- coding: utf-8 -*-
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
    pyudev
    ======

    A binding to libudev_.

    .. _libudev: http://www.kernel.org/pub/linux/utils/kernel/hotplug/udev.html

    Usage
    -----

    The library context
    ^^^^^^^^^^^^^^^^^^^

    First import :mod:`pyudev` and create a :class:`Context` object.  This
    object is mandatory to use this library:

    >>> import pyudev
    >>> context = pyudev.Context()

    Listing devices
    ^^^^^^^^^^^^^^^

    The :class:`Context` provides access to the list of all devices through
    :meth:`Context.list_devices`:

    >>> devices = context.list_devices()

    ``devices`` is an instance of :class:`Enumerator`.  This class provides
    some methods to filter the list of devices.  You can filter by specific
    subsystems and by properties.  For instance, the following code only
    matches all mouse devices:

    >>> devices = devices.match_subsystem('input').match_property(
    ...     'ID_INPUT_MOUSE', True)

    Once the (optional) filters are applied, you can iterate over
    ``devices``.  This yields :class:`Device` objects, which provide various
    attributes to access information:

    >>> for device in devices:
    ...     if device.sys_name.startswith('event'):
    ...         device.parent['NAME']
    ...
    u'"Logitech USB-PS/2 Optical Mouse"'
    u'"Broadcom Corp"'
    u'"PS/2 Mouse"'

    Monitoring devices
    ^^^^^^^^^^^^^^^^^^

    Alternatively you can monitor the device tree for changes instead of
    listing all devices using the :class:`Monitor` class:

    >>> monitor = pyudev.Monitor.from_netlink(context)
    >>> monitor.filter_by(subsystem='input')
    >>> for action, device in monitor:
    ...     if action == 'add':
    ...         print('{0!r} added'.format(device))

    Accessing devices directly
    ^^^^^^^^^^^^^^^^^^^^^^^^^^

    If you are interested in a specific device, whose name or whose path is
    known to you, you can construct a :class:`Device` object directly,
    either with from a device path:

    >>> platform_device = pyudev.Device.from_path(
    ...     context, '/sys/devices/platform')
    >>> platform_device
    Device(u'/sys/devices/platform')
    >>> platform_device.sys_name
    u'platform'

    Or from a subsystem and a device name:

    >>> sda = pyudev.Device.from_name(context, 'block', 'sda')
    >>> sda.subsystem
    u'block'
    >>> sda.sys_name
    u'sda'

    Device information
    ^^^^^^^^^^^^^^^^^^

    In either case, you get :class:`Device` objects, which are really the
    central objects in pyudev, because they give access to everything you
    ever wanted to know about devices.

    The :class:`Device` class implements the ``Mapping`` ABC, and thus
    behaves like a read-only dictionary.  It maps the names of general UDev
    properties to the corresponding values.  You can use all the well-known
    dictionary methods to access device information.

    Aside of dictionary access, some special properties are available, that
    provide access to udev properties and attributes of the device (like its
    path in ``sysfs``, which is available through
    :attr:`Device.device_path`).

    One important property is :attr:`Device.attributes`, which gives you a
    dictionary containing the system attributes of the device.  A system
    attribute is basically just a file inside the device directory.  These
    attributes contain device-specific information about the device (in
    contrast to the general UDev properties).

    Toolkit integration
    ^^^^^^^^^^^^^^^^^^^

    pyudev provides classes, which integrate monitoring into the event loop
    of GUI toolkits.  Currently, only PyQt4 and PySide are supported.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import absolute_import


__version__ = '0.6'
__all__ = ['Context', 'Device']


from pyudev.core import *
from pyudev.monitor import *
