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

    Usage
    -----

    The central class is the :class:`Context`.  An instance of this class is
    mandatory to use any function of this library:

    >>> context = Context()

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

    >>> monitor = Monitor.from_netlink(context)
    >>> monitor.filter_by(subsystem='input')
    >>> for action, device in monitor:
    ...     if action == 'add':
    ...         print device, 'added'


    Remarks
    -------

    If imported with wildcard (``from udev import *``), only :class:`Device`
    and :class:`Context` will be imported.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

import sys
import select
from itertools import count
from collections import Mapping
from contextlib import closing

import _udev


__version__ = '0.2'
__all__ = ['Context', 'Device']


libudev = _udev.load_udev_library()



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
    Enumerate all available devices.

    To retrieve devices, simply iterate over an instance of this class.
    This operation yields :class:`Device` objects representing the available
    devices.

    Before iteration the device list can be filtered by subsystem or by
    property values using :meth:`match_subsystem` and
    :meth:`match_property`.  All added filters must match for a device to be
    included in the device list, when eventually iterating over this object.
    The filter methods return the instance itself again, thus supporting
    method chaining to apply many filters in a row.

    Once a filter was added, it cannot be removed.  Create a new object
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

    def __del__(self):
        libudev.udev_enumerate_unref(self._enumerator)

    def match_subsystem(self, subsystem):
        """
        Include all devices, which are part of the given ``subsystem``.

        ``subsystem`` is either a unicode string or a byte string,
        containing the name of the subsystem.

        Return the instance again.
        """
        _check_call(libudev.udev_enumerate_add_match_subsystem,
                    self._enumerator, _assert_bytes(subsystem))
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
        _check_call(libudev.udev_enumerate_add_match_property,
                    self._enumerator, _assert_bytes(property),
                    _property_value_to_bytes(value))
        return self

    def __iter__(self):
        """
        Iterate over all matching devices.

        Yield :class:`Device` objects.
        """
        _check_call(libudev.udev_enumerate_scan_devices, self._enumerator)
        entry = libudev.udev_enumerate_get_list_entry(self._enumerator)
        for name in _udev_list_iterate(entry):
            yield Device.from_sys_path(self.context, name)


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

    Devices can compare equal and unequal to other devices and to strings
    (based on :attr:`device_path`).  Moreover devices are hashable.  Therefore
    :class:`Device` objects can be used as keys in dictionaries and sets.
    """

    @classmethod
    def from_sys_path(cls, context, sys_path):
        """
        Create a new device from a given ``sys_path``.

        ``context`` is the :class:`Context` in which to search the device.
        ``sys_path`` is a unicode or byte string containing the path of the
        device inside ``sysfs`` with the mount point included.

        Return a :class:`Device` object for the device, or ``None``, if no
        device existed at ``sys_path``.
        """
        if not isinstance(context, Context):
            raise TypeError('Invalid context object')
        device = libudev.udev_device_new_from_syspath(
            context._context, _assert_bytes(sys_path))
        if not device:
            return None
        return cls(context, device)

    def __init__(self, context, _device):
        self.context = context
        self._device = _device

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
        Device file name inside ``sysfs`` unicode string.
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
        for name in _udev_list_iterate(entry):
            yield name.decode(sys.getfilesystemencoding())

    def __iter__(self):
        """
        Iterate over the names of all properties defined for this device.
        Property names are unicode strings.
        """
        entry = libudev.udev_device_get_properties_list_entry(self._device)
        for name in _udev_list_iterate(entry):
            yield name.decode(sys.getfilesystemencoding())

    def __len__(self):
        """
        Return the amount of properties defined for this device.
        """
        entry = libudev.udev_device_get_properties_list_entry(self._device)
        counter = count()
        for _ in _udev_list_iterate(entry):
            next(counter)
        return next(counter)

    def __getitem__(self, property):
        """
        Get the given ``property`` from this device.

        ``property`` is a unicode or byte string containing the name of the
        property.

        Return the property as integer or string, or raise a
        :exc:`~exceptions.KeyError`, the the given property is not defined
        for this device.
        """
        value = libudev.udev_device_get_property_value(
            self._device, _assert_bytes(property))
        if value is None:
            raise KeyError('No such property: {0}'.format(property))
        return _property_value_from_bytes(value)

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


class Monitor(object):
    """
    Monitor udev events:

    >>> context = Context()
    >>> monitor = Monitor.from_netlink(context)
    >>> monitor.filter_by(subsystem='input')
    >>> for action, device in monitor:
    ...     print action, device
    ...

    A :class:`Monitor` objects connects to the udev daemon and listens for
    changes to the device list.  A monitor is created by connecting to the
    kernel daemon through netlink (see :meth:`from_netlink`).
    Alternatively, connections to arbitrary daemons can be made using
    :meth:`from_socket`, which is however only seldom of use.

    Once the monitor is created, you can add a filter using
    :meth:`filter_by` to drop incoming events in subsystems, which are not
    of interest to the application.

    If the monitor is eventually set up, you can either iterate over the
    :class:`Monitor` object.  In this case, the monitor implicitly starts
    listening, and polls for incoming events.  Such events are then yielded
    to the caller.  Iteration is a blocking operation and does not integrate
    into external event loops.  If such integration is required, you can
    explicitly enable the monitor (see :meth:`enable_receiving`), and then
    retrieve a file description using :meth:`fileno`.  This file descriptor
    can then be passed to classes like ``QSocketNotifier`` from Qt4.
    """

    def __init__(self, context, monitor_p):
        self.context = context
        self._monitor = monitor_p

    def __del__(self):
        libudev.udev_monitor_unref(self._monitor)

    @classmethod
    def from_netlink(cls, context, source='udev'):
        """
        Create a monitor by connecting to the kernel daemon through netlink.

        ``context`` is the :class:`Context` to use.  ``source`` is the event
        source.  As of now, two sources are available:

        - ``'udev'`` (the default):  Events emitted after udev as registered
          and configured the device.  This is the absolutely recommended
          source for applications.
        - ``'kernel'``:  Events emitted directly after the kernel has seen
          the device.  The device has not yet been configured by udev and
          might not be usable at all.  **Never** use this, unless you know
          what you are doing.

        Return a new :class:`Monitor` object, which is connected to the
        given source.  Raise :exc:`~exceptions.ValueError`, if an invalid
        source has been specified.  Raise
        :exc:`~exceptions.EnvironmentError`, if the creation of the monitor
        failed.
        """
        if source not in ('kernel', 'udev'):
            raise ValueError('Invalid source: {0!r}. Must be one of "udev" '
                             'or "kernel"'.format(source))
        source = _assert_bytes(source)
        monitor = libudev.udev_monitor_new_from_netlink(
            context._context, source)
        if not monitor:
            raise EnvironmentError('Could not create udev monitor')
        return cls(context, monitor)

    @classmethod
    def from_socket(cls, context, socket_path):
        """
        Connect to an arbitrary udev daemon using the given ``socket_path``.

        ``context`` is the :class:`Context` to use. ``socket_path`` is
        string, pointing to an existing socket.  If the path starts with a
        @, use an abstract namespace socket.  If ``socket_path`` does not
        exist, fall back to an abstract namespace socket.

        The caller is responsible for permissions and cleanup of the socket
        file.

        Return a new :class:`Monitor` object, which is connected to the
        given socket.  Raise :exc:`~exceptions.EnvironmentError`, if the
        creation of the monitor failed.
        """
        socket_path = _assert_bytes(socket_path)
        monitor = libudev.udev_monitor_new_from_socket(
            context._context, source)
        if not monitor:
            raise EnvironmentError('Could not create udev monitor')
        return cls(context, monitor)

    def fileno(self):
        """
        Return the file description associated with this monitor as integer.

        This is really a real file descriptor ;), which can be watched and
        :func:`select.select`\ ed.
        """
        return libudev.udev_monitor_get_fd(self._monitor)

    def filter_by(self, subsystem=None, device_type=None):
        """
        Filter incoming events.

        ``subsystem`` can either be ``None`` to not filter against any
        specific subsystem, or a byte or unicode string with the name of a
        subsystem (e.g. ``'input'``).  In the latter case, only events
        originating from the given subsystem pass the filter and are given
        to the caller.

        ``device_type`` can either be ``None`` to not filter against any
        specific type of device, or a byte or unicode string specifying the
        device type.  In the latter case, only events originating from
        devices with the given type pass the filter and are given to the
        caller.

        If both arguments are specified, only events from the given
        subsystem *and* with the given device type are accepted.

        This method must be called *before* :meth:`enable_receiving`.

        Raise :exc:`~exceptions.EnvironmentError`, if the filter could not
        be installed.
        """
        if subsystem:
            subsystem = _assert_bytes(subsystem)
        if device_type:
            device_type = _assert_bytes(device_type)
        error = libudev.udev_monitor_filter_add_match_subsystem_devtype(
            self._monitor, subsystem, device_type)
        if error:
            raise EnvironmentError('Could not install filter on monitor')

    def enable_receiving(self):
        """
        Switch the monitor into listing mode.

        Connect to the event source and receive incoming events.  Only after
        calling this method, the monitor listens for incoming events.

        .. note::

           This method is implicitly called by :meth:`__iter__`.  You don't
           need to call it explicitly, if you are iterating over the
           monitor.
        """
        error = libudev.udev_monitor_enable_receiving(self._monitor)
        if error:
            raise EnvironmentError('Could not put monitor into '
                                   'receiving mode')

    start = enable_receiving

    def receive_device(self):
        """
        Receive a single device from the monitor.

        The caller must make sure, that there are events available in the
        event queue.  The call may block, until a device is available.

        If a device was available, return ``(action, device)``.  ``action``
        is a string describing the action (e.g. ``'add'``, ``'remove'``).
        ``device`` is :class:`Device` object describing the device.  If no
        device was available, return ``None``.
        """
        device_p = libudev.udev_monitor_receive_device(self._monitor)
        if not device_p:
            return None
        action = libudev.udev_device_get_action(device_p).decode(
            sys.getfilesystemencoding())
        return action, Device(self.context, device_p)

    def __iter__(self):
        """
        Wait for incoming events and receive them upon arrival.

        This methods implicitly calls :meth:`enable_receiving`, and starts
        polling the :meth:`fileno` of this monitor.  If a event comes in, it
        receives the corresponding device and yields it to the caller.

        The returned iterator is endless, and continues receiving devices
        without ever stopping.

        Yields ``(action, device)`` (see :meth:`receive_device` for a
        description).
        """
        self.enable_receiving()
        with closing(select.epoll()) as notifier:
            notifier.register(self, select.EPOLLIN)
            while True:
                events = notifier.poll()
                if events:
                    yield self.receive_device()

