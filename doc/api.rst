:mod:`udev` – pyudev API
========================

.. automodule:: udev
   :platform: Linux
   :synopsis: libudev bindings


:class:`Context` – the central object
-------------------------------------

.. autoclass:: Context

   .. automethod:: __init__

   .. autoattribute:: sys_path

   .. autoattribute:: device_path

   .. automethod:: list_devices


:class:`Enumerator` – listing devices
-------------------------------------

.. autoclass:: Enumerator

   .. automethod:: match_subsystem

   .. automethod:: match_property

   .. automethod:: match_children

   .. automethod:: __iter__


:class:`Device` – accessing device information
----------------------------------------------

.. autoclass:: Device

   .. automethod:: from_sys_path

   .. autoattribute:: sys_path

   .. autoattribute:: sys_name

   .. autoattribute:: device_path

   .. autoattribute:: subsystem

   .. autoattribute:: device_node

   .. autoattribute:: device_links

   .. autoattribute:: parent

   .. autoattribute:: children

   .. automethod:: traverse

   .. automethod:: __iter__

   .. automethod:: __len__

   .. automethod:: __getitem__

   .. automethod:: asint

   .. automethod:: asbool


:class:`Monitor` – monitor devices
----------------------------------

.. autoclass:: Monitor

   .. automethod:: from_netlink

   .. automethod:: from_socket

   .. automethod:: fileno

   .. automethod:: filter_by

   .. automethod:: enable_receiving

   .. method:: start

      Alias for :meth:`enable_receiving`

   .. automethod:: receive_device

   .. automethod:: __iter__


:mod:`qudev` – Py4Qt integration
================================

.. module:: qudev
   :platform: Linux
   :synopsis: PyQt4 binding to :mod:`udev`

If you already have an existing context or monitor object and simply want to
plug the monitoring into the Qt event loop, use
:class:`QUDevMonitorObserver`:

.. autoclass:: QUDevMonitorObserver

   .. automethod:: __init__

   .. pyqt4:signal:: deviceEvent(action, device)

      Emitted upon any device event.  ``action`` is a unicode string
      containing the action name, and ``device`` is the
      :class:`~udev.Device` object describing the device.

      The arguments of this signal are basically the return value of
      :meth:`~udev.Monitor.receive_device`

   .. pyqt4:signal:: deviceAdded(device)

      Emitted if a :class:`~udev.Device` is added (e.g a USB device was
      plugged).

   .. pyqt4:signal:: deviceRemoved(device)

      Emitted if a :class:`~udev.Device` is removed (e.g. a USB device was
      unplugged).

   .. pyqt4:signal:: deviceChanged(device)

      Emitted if a :class:`~udev.Device` was somehow changed (e.g. a change
      of a property)

   .. pyqt4:signal:: deviceMoved(device)

      Emitted if a :class:`~udev.Device` was renamed, moved or re-parented.
