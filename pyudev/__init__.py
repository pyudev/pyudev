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


"""
    pyudev
    ======

    A binding to ``libudev``.

    Usage
    -----

    First import :mod:`pyudev` and create a :class:`Context` object.  This
    object is mandatory to use this library:

    >>> import pyudev
    >>> context = pyudev.Context()

    .. note::

       ``import pyudev`` is the preferred way to load :mod:`pyudev`. All
       classes and sub-modules are available directly in the :mod:`pyudev`
       namespace, so you can just do:

       >>> import pyudev
       >>> observer = pyudev.pyqt4.QUDevMonitorObserver(monitor)

       Thanks to apipkg_ this just works :). The ``pyqt4`` module is
       lazy-loaded automatically without any additional imports.

       .. _apipkg: http://pypi.python.org/pypi/apipkg/

    A :class:`Context` instance provides access to some basic udev
    properties:

    >>> context.device_path
    u'/dev'
    >>> context.sys_path
    u'/sys'

    But most importantly, the context provides access to the list of all
    available devices through :meth:`Context.list_devices`:

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

    :class:`Device` implements the ``Mapping`` ABC, and thus behaves like a
    read-only dictionary, mapping the names of udev properties to the
    corresponding values.  This means, that you can use the well-known
    dictionary methods to access device information.

    Aside of dictionary access, some special properties are available, that
    provide access to udev attributes of the device (like its path in
    ``sysfs``).

    You can not only list existing devices, you can also monitor the device
    list for changes using the :class:`Monitor` class:

    >>> monitor = pyudev.Monitor.from_netlink(context)
    >>> monitor.filter_by(subsystem='input')
    >>> for action, device in monitor:
    ...     if action == 'add':
    ...         print device, 'added'

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import absolute_import


__version__ = '0.5'
__all__ = ['Context', 'Device']


import apipkg
apipkg.initpkg(
    __name__, dict(
        __doc__='.:__doc__',
        Context='._core:Context',
        Device='._core:Device',
        NoSuchDeviceError='._core:NoSuchDeviceError',
        Monitor='._monitor:Monitor',
        Enumerator='._core:Enumerator',
        pyqt4=dict(
            QUDevMonitorObserver='._pyqt4:QUDevMonitorObserver',
            )
        ),
    )

