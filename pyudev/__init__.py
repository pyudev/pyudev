# -*- coding: utf-8 -*-
# Copyright (C) 2010, 2011, 2012 Sebastian Wiesner <lunaryorn@googlemail.com>

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

    .. _libudev: http://www.kernel.org/pub/linux/utils/kernel/hotplug/libudev/

    Usage
    -----

    To use :mod:`pyudev`, simply import it:

    >>> import pyudev
    >>> pyudev.__version__
    '0.8'
    >>> pyudev.udev_version()
    165

    With the exception of the toolkit integration all classes and functions are
    available in the top-level namespace of :mod:`pyudev`.

    The library context
    ^^^^^^^^^^^^^^^^^^^

    To use these classes and functions, a :class:`Context` object is required:

    >>> context = pyudev.Context()

    You can see this object as some kind of connection to the udev database,
    through which the contents of this database can be queried.

    Listing devices
    ^^^^^^^^^^^^^^^

    The :class:`Context` provides access to the list of all devices through
    :meth:`Context.list_devices`:

    >>> devices = context.list_devices()

    You can filter the devices by specific subsystems or properties.  For
    instance, the following code only matches all mouse devices:

    >>> devices = context.list_devices(subsystem='input', ID_INPUT_MOUSE=True)

    In both cases ``devices`` is an instance of :class:`Enumerator`.  When
    iterated over, this class yields :class:`Device` objects, representing
    those devices, which match the filters.  :class:`Device` objects provide
    various attributes to access information:

    >>> for device in devices:
    ...     if device.sys_name.startswith('event'):
    ...         device.parent['NAME']
    ...
    u'"Logitech USB-PS/2 Optical Mouse"'
    u'"Broadcom Corp"'
    u'"PS/2 Mouse"'

    Monitoring devices
    ^^^^^^^^^^^^^^^^^^

    Instead of listing devices, you can monitor the device tree for changes
    using the :class:`Monitor` class:

    >>> monitor = pyudev.Monitor.from_netlink(context)
    >>> monitor.filter_by(subsystem='input')
    >>> for action, device in monitor:
    ...     if action == 'add':
    ...         print('{0!r} added'.format(device))

    To conveniently observe monitors in background, the
    :class:`MonitorObserver` class is provided, which implements a background
    thread that continously receives events from a :class:`Monitor`.

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

    pyudev provides classes, which integrate monitoring into the event loop of
    GUI toolkits.  Currently, PyQt4, PySide, pygobject and wx are supported.


    A note on versioning
    --------------------

    :mod:`pyudev` tries to provide all features of recent udev versions, while
    maintaining compatibility with older versions.  This means, that some
    attributes of :mod:`pyudev` classes are not available, if udev is too old.
    Whenever this is the case, the minimum version of udev required to use the
    attribute is described in the documentation, see for instance
    :attr:`Device.is_initialized`.  If no specific version is mentioned, the
    attribute is available from udev 151 onwards, which is the oldest udev
    version supported by :mod:`pyudev`.  udev 150 and earlier may work with
    :mod:`pyudev`, but are not tested and consequently not officially
    supported.

    You can use :func:`udev_version()` to check the version of udev and see, if
    it is recent enough for your needs:

    >>> if pyudev.udev_version() < 165:
    ...     print('udev is somewhat older here')
    ... else:
    ...     print('udev is quite up to date here')
    ...
    udev is quite up to date here

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)


__version__ = '0.14'
__version_info__ = tuple(map(int, __version__.split('.')))
__all__ = ['Context', 'Device']


from pyudev.device import *
from pyudev.core import *
from pyudev.monitor import *
