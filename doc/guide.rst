User guide
==========

.. currentmodule:: pyudev

This guide gives an introduction in how to use pyudev for common operations
like device enumeration or monitoring.  A detailled reference is provided in
the :doc:`API documentation <api/index>`.


Installation
------------

Before we can start, you need to install pyudev from PyPI_::

   pip install pyudev

No compiler and no library headers required, because pyudev is implemented in
pure Python thanks to :mod:`ctypes`.


Getting started
---------------

Now you can import pyudev and do some version checks:

>>> import pyudev
>>> pyudev.__version__
u'0.15'
>>> pyudev.udev_version()
181


A note on versioning
--------------------

pyudev supports libudev_ 151 or newer, but still tries to cover the most recent
libudev_ API completely.  If you are using older libudev_ releases, some
functionality of pyudev may be unavailable, simply because libudev_ is too old
to support a specific feature.  Whenever this is the case, the minimum required
version of udev is noted in the documentation (see
:attr:`Device.is_initialized` for an example).  If no version is specified for
an attribute or a method, it is available on all supported libudev_ versions.
You can check the version of the underlying libudev_ with
:func:`pyudev.udev_version()`.


Enumerating devices
-------------------

To enumerate devices, you need to establish a "connection" to the udev device
database first.  This connection is represented by a library :class:`Context`:

>>> context = pyudev.Context()

This object provides general information about the udev database, like the
device node directory and the ``sysfs`` mount point:

>>> context.device_path
u'/dev'
>>> context.sys_path
u'/sys'

It's main purpose however is to provide access to the device database:

>>> for device in context.list_devices(): # doctest: +ELLIPSIS
...     device
...
Device(u'/sys/devices/LNXSYSTM:00')
Device(u'/sys/devices/LNXSYSTM:00/LNXCPU:00')
Device(u'/sys/devices/LNXSYSTM:00/LNXCPU:01')
...

You can filter the devices with keyword arguments to
:meth:`~Context.list_devices()`.  The following code enumerates all partitions:

>>> for device in context.list_devices(subsystem='block', DEVTYPE='partition'):
...    print(device)
...
Device(u'/sys/devices/pci0000:00/0000:00:0d.0/host2/target2:0:0/2:0:0:0/block/sda/sda1')
Device(u'/sys/devices/pci0000:00/0000:00:0d.0/host2/target2:0:0/2:0:0:0/block/sda/sda2')
Device(u'/sys/devices/pci0000:00/0000:00:0d.0/host2/target2:0:0/2:0:0:0/block/sda/sda3')

:meth:`~Context.list_devices()` returns an :class:`Enumerator` object.  This
object represents a filtered list of devices.  Iterating over this object
yields :class:`Device` objects which represent individual devices.

The choice of the right filters requires some knowledge about the way udev
classifies and categorizes devices.  Poke around in ``/sys/`` to get a feeling
for the udev-way to handle devices.


Accessing individual devices directly
-------------------------------------

If you just need a single specific :class:`Device`, you don't need to enumerate
all devices with a specific filter criterion.  Instead, just get the device
object directly either by its device path (:meth:`Device.from_path()`), or by
the its subsystem and device name (:meth:`Device.from_name()`).  The following
code gets the :class:`Device` object for the first hard disc in two different
ways:

>>> pyudev.Device.from_path(context, '/sys/block/sda')
Device(u'/sys/devices/pci0000:00/0000:00:0d.0/host2/target2:0:0/2:0:0:0/block/sda')
>>> pyudev.Device.from_name(context, 'block', 'sda')
Device(u'/sys/devices/pci0000:00/0000:00:0d.0/host2/target2:0:0/2:0:0:0/block/sda')

As you can see, you need to pass a :class:`Context` to both methods as
reference to the udev database from which to retrieve information about the
device.

.. note::

   The :class:`Device` objects created in the above example refer to the same
   device.  Consequently, they are considered equal:

   >>> pyudev.Device.from_path(context, '/sys/block/sda') == pyudev.Device.from_name(context, 'block', 'sda')
   True

   Whereas :class:`Device` objects referring to different devices are unequal:

   >>> pyudev.Device.from_name(context, 'block', 'sda') == pyudev.Device.from_name(context, 'block', 'sda1')
   False


Querying device information
---------------------------

A :class:`Device` has a set of "device properties" (not to be confused with
Python properties as created by :func:`property()`) that describe the
capabilities and features of this device as well as its relationship to other
devices.

Common device properties are available as properties of a :class:`Device`
object.  For instance, you can directly query the :attr:`device_node` and the
:attr:`device_type` of block devices:

>>> for device in context.list_devices(subsystem='block'):
...     print('{0} ({1})'.format(device.device_node, device.device_type))
...
/dev/sr0 (disk)
/dev/sda (disk)
/dev/sda1 (partition)
/dev/sda2 (partition)
/dev/sda3 (partition)

For all other properties, :class:`Device` provides a dictionary-like interface
to directly access the device properties.  You'll get the same information has
with the generic properties:

>>> for device in context.list_devices(subsystem='block'):
...    print('{0} ({1})'.format(device['DEVNAME'], device['DEVTYPE']))
...
/dev/sr0 (disk)
/dev/sda (disk)
/dev/sda1 (partition)
/dev/sda2 (partition)
/dev/sda3 (partition)

.. warning::

   When filtering devices, you have to use the device property names.  The
   names of corresponding properties of :class:`Device` will generally **not**
   work.  Compare the following two statements:

   >>> [device.device_node for device in context.list_devices(subsystem='block', DEVTYPE='partition')]
   [u'/dev/sda1', u'/dev/sda2', u'/dev/sda3']
   >>> [device.device_node for device in context.list_devices(subsystem='block', device_type='partition')]
   []


But you can also query many device properties that are not available as Python
properties on the :class:`Device` object with a convenient mapping interface,
like the filesystem type.  :class:`Device` provides a convenient mapping
interface for this purpose:

>>> for device in context.list_devices(subsystem='block', DEVTYPE='partition'):
...     print('{0} ({1})'.format(device.device_node, device.get('ID_FS_TYPE')))
...
/dev/sda1 (ext3)
/dev/sda2 (swap)
/dev/sda3 (ext4)

.. note::

   Such device specific properties may not be available on devices.  Either use
   ``get()`` to specify default values for missing properties, or be prepared
   to catch :exc:`~exceptions.KeyError`.

Most device properties are computed by udev rules from the driver- and
device-specific "device attributes".  The :attr:`Device.attributes` mapping
gives you access to these attributes, but generally you should not need these.
Use the device properties whenever possible.


Examing the device hierarchy
----------------------------

Udev stores devices in a tree-like structure, where many devices have a
:attr:`~Device.parent` device that more or less resembles the physical
relationship between devices.  For instance, the :attr:`~Device.parent` of
partition devices is the :class:`Device` object that represents the disc these
partitions are located on:

>>> for device in context.list_devices(subsystem='block', DEVTYPE='partition'):
...    print('{0} is located on {1}'.format(device.device_node, device.parent.device_node))
...
/dev/sda1 is located on /dev/sda
/dev/sda2 is located on /dev/sda
/dev/sda3 is located on /dev/sda

Generally, you should not rely on the direct parent-child relationship between
two devices.  Instead of accessing the parent directly, search for a parent
within a specific subsystem, e.g. for the parent ``block`` device, with
:meth:`~Device.find_parent()`:

>>> for device in context.list_devices(subsystem='block', DEVTYPE='partition'):
...    print('{0} is located on {1}'.format(device.device_node, device.find_parent('block').device_node))
...
/dev/sda1 is located on /dev/sda
/dev/sda2 is located on /dev/sda
/dev/sda3 is located on /dev/sda

This also save you the tedious work of traversing the device tree manually, if
you are interested in grand parents, like the name of the PCI slot of the SCSI
or IDE controller of the disc that contains a partition:

>>> for device in context.list_devices(subsystem='block', DEVTYPE='partition'):
...    print('{0} attached to PCI slot {1}'.format(device.device_node, device.find_parent('pci')['PCI_SLOT_NAME']))
...
/dev/sda1 attached to PCI slot 0000:00:0d.0
/dev/sda2 attached to PCI slot 0000:00:0d.0
/dev/sda3 attached to PCI slot 0000:00:0d.0


Monitoring devices
------------------

Synchronous monitoring
~~~~~~~~~~~~~~~~~~~~~~

The Linux kernel emits events whenever devices are added, removed (e.g. a USB
stick was plugged or unplugged) or have their attributes changed (e.g. the
charge level of the battery changed).  With :class:`pyudev.Monitor` you can
react on such events, for example to react on added or removed mountable
filesystems:

>>> monitor = pyudev.Monitor.from_netlink(context)
>>> monitor.filter_by('block')
>>> for action, device in monitor:
...     if 'ID_FS_TYPE' in device:
...         print('{0} partition {1}'.format(action, device.get('ID_FS_LABEL')))
...
add partition MULTIBOOT
remove partition MULTIBOOT

After construction of a monitor, you can install an event filter on the monitor
using :meth:`~Monitor.filter_by()`.  In the above example only events from the
``block`` subsystem are handled.

.. note::

   Always prefer :meth:`~Monitor.filter_by()` and
   :meth:`~Monitor.filter_by_tag()` over manually filtering devices (e.g. by
   `device.subsystem == 'block'`` or ``tag in device.tags``).  These methods
   install the filter on the *kernel side*.  A process waiting for events is
   thus only woken up for events that match these filters.  This is much nicer
   in terms of power consumption and system load than executing filters in the
   process itself.

Eventually, you can receive events from the monitor.  As you can see, a
:class:`Monitor` is iterable and synchronously yields occurred events.  If you
iterate over a :class:`Monitor`, you will synchronously receive events in an
endless loop, until you raise an exception, or ``break`` the loop.  While this
is sufficient for quick and dirty scripts, typically more sophisticated control
of monitoring is required.


Asynchronous monitoring
~~~~~~~~~~~~~~~~~~~~~~~

For this purpose, pyudev provides asynchronous monitoring with
:class:`MonitorObserver`:

>>> monitor = pyudev.Monitor.from_netlink(context)
>>> monitor.filter_by('block')
>>> def log_event(action, device):
...    if 'ID_FS_TYPE' in device:
...        with open('filesystems.log', 'a+') as stream:
...            print('{0} - {1}'.format(action, device.get('ID_FS_LABEL')), file=stream)
...
>>> observer = pyudev.MonitorObserver(monitor, log_event)
>>> observer.start()

Once the ``observer`` is started, the ``log_event()`` is invoked asynchronously
for every event emitted by the ``monitor``.

.. warning::

   The callback is invoked from a *different* thread than the one in which the
   ``observer`` was created.  Be sure to protect access to shared resource
   properly when you access them from the callback (e.g. by locking).

You can stop :class:`MonitorObserver` objects again, if you don't need them any
longer:

>>> observer.stop()
>>> observer.join()


.. _pypi: https://pypi.python.org/pypi/pyudev
.. _libudev: http://www.kernel.org/pub/linux/utils/kernel/hotplug/libudev/
