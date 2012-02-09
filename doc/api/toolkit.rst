Toolkit integration
===================

Qt integration
--------------

To plug monitoring with :class:`pyudev.Monitor` into the Qt event loop, so
that Qt signals are asynchronously emitted upon events,
:class:`QUDevMonitorObserver` is provided:

.. class:: QUDevMonitorObserver

   Observe a :class:`~pyudev.Monitor` and emit Qt signals upon device
   events:

   >>> context = pyudev.Context()
   >>> monitor = pyudev.Monitor.from_netlink(context)
   >>> monitor.filter_by(subsystem='input')
   >>> observer = QUDevMonitorObserver(monitor)
   >>> def device_connected(device):
   ...     print('{0!r} added'.format(device))
   >>> observer.deviceAdded.connect(device_connected)
   >>> monitor.start()

   This class is a child of :class:`QtCore.QObject`.

   .. method:: __init__(monitor, parent=None)

      Observe the given ``monitor`` (a :class:`pyudev.Monitor`).

      ``parent`` is the parent :class:`~QtCore.QObject` of this object.  It
      is passed straight to the inherited constructor of
      :class:`~QtCore.QObject`.

   .. attribute:: monitor

      The :class:`~pyudev.Monitor` observed by this object.

   .. attribute:: notifier

      The underlying :class:`QtCore.QSocketNotifier` used to watch the
      :attr:`monitor`

   .. rubric:: Signals

   This class defines the following Qt signals:

   .. method:: deviceEvent(action, device)

      Emitted upon any device event.  ``action`` is a unicode string
      containing the action name, and ``device`` is the
      :class:`~pyudev.Device` object describing the device.

      Basically the arguments of this signal are simply the return value of
      :meth:`~pyudev.Monitor.receive_device`

   .. method:: deviceAdded(device)

      Emitted if a :class:`~pyudev.Device` is added (e.g a USB device was
      plugged).

   .. method:: deviceRemoved(device)

      Emitted if a :class:`~pyudev.Device` is removed (e.g. a USB device was
      unplugged).

   .. method:: deviceChanged(device)

      Emitted if a :class:`~pyudev.Device` was somehow changed (e.g. a
      change of a property)

   .. method:: deviceMoved(device)

      Emitted if a :class:`~pyudev.Device` was renamed, moved or
      re-parented.


Currently there are two different, incompatible bindings to Qt4:

PyQt4_
   Older, more mature, but developed by a 3rd party (Riverbank computing)
   and distributed under the GPL (though with some exceptions for other free
   software licences)

PySide_
   Developed by Nokia as alternative to PyQt4_ and distributed under the
   less restrictive LGPL, however not yet as mature and feature-rich as
   PyQt4_.

For both of these bindings a :class:`QUDevMonitorObserver` implementation is
provided, each in a separate module:

:mod:`pyudev.pyqt4`
^^^^^^^^^^^^^^^^^^^

.. automodule:: pyudev.pyqt4
   :platform: Linux
   :synopsis: PyQt4 integration

.. class:: QUDevMonitorObserver

   A :class:`QUDevMonitorObserver` implementation for PyQt4_

:mod:`pyudev.pyside`
^^^^^^^^^^^^^^^^^^^^

.. automodule:: pyudev.pyside
   :platform: Linux
   :synopsis: PySide integration

.. class:: QUDevMonitorObserver

   A :class:`QUDevMonitorObserver` implementation for PySide_


:mod:`pyudev.glib` – Glib and Gtk integration
---------------------------------------------

.. automodule:: pyudev.glib
   :platform: Linux
   :synopsis: Glib integration

.. autoclass:: GUDevMonitorObserver

   .. attribute:: monitor

      The :class:`~pyudev.Monitor` observed by this object.

   .. attribute:: event_source

      The event source, which represents the watch on the :attr:`monitor`
      (as returned by :func:`glib.io_add_watch`).  Can be passed to
      :func:`glib.source_remove` to stop observing the monitor.

   .. rubric:: Signals

   This class defines the following GObject signals:

   .. method:: device-event(observer, action, device)

      Emitted upon any device event.  ``observer`` is the
      :class:`GUDevMonitorObserver`, which emitted the signal.  ``action``
      is a unicode string containing the action name, and ``device`` is the
      :class:`~pyudev.Device`, which caused this event.

      Basically the last two arguments of this signal are simply the
      return value of :meth:`~pyudev.Monitor.receive_device`

   .. method:: device-added(observer, device)

      Emitted if a :class:`~pyudev.Device` is added (e.g a USB device was
      plugged).

   .. method:: device-removed(observer, device)

      Emitted if a :class:`~pyudev.Device` is removed (e.g. a USB device was
      unplugged).

   .. method:: device-changed(observer, device)

      Emitted if a :class:`~pyudev.Device` was somehow changed (e.g. a
      change of a property)

   .. method:: device-moved(observer, device)

      Emitted if a :class:`~pyudev.Device` was renamed, moved or
      re-parented.

:mod:`pyudev.wx` – wxWidgets integration
---------------------------------------------

.. automodule:: pyudev.wx
   :platform: Linux
   :synopsis: wxWidgets integration

.. autoclass:: WxUDevMonitorObserver

   .. attribute:: monitor

      The :class:`~pyudev.Monitor` observed by this object.

   .. autoattribute::  enabled


.. rubric:: Event constants

:class:`WxUDevMonitorObserver` exposes the following events:

.. data:: EVT_DEVICE_EVENT

   Emitted upon any device event.  Receivers get a :class:`DeviceEvent` object
   as argument.

.. data:: EVT_DEVICE_ADDED

   Emitted if a :class:`~pyudev.Device` is added (e.g a USB device was
   plugged).  Receivers get a :class:`DeviceAddedEvent` object as argument.

.. data:: EVT_DEVICE_REMOVED

   Emitted if a :class:`~pyudev.Device` is removed (e.g. a USB device was
   unplugged).  Receivers get a :class:`DeviceRemovedEvent` object as argument.

.. data:: EVT_DEVICE_CHANGED

   Emitted if a :class:`~pyudev.Device` was somehow changed (e.g. a change of a
   property).  Receivers get a :class:`DeviceChangedEvent` object as argument.

.. data:: EVT_DEVICE_MOVED

   Emitted if a :class:`~pyudev.Device` was renamed, moved or re-parented.
   Receivers get a :class:`DeviceMovedEvent` object as argument.


.. rubric:: Event objects

.. class:: DeviceEvent

   Argument object for :data:`EVT_DEVICE_EVENT`.

   .. attribute:: action

      A unicode string containing the action name.

   .. attribute:: device

      The :class:`~pyudev.Device` object that caused this event.


.. class:: DeviceAddedEvent
           DeviceRemovedEvent
           DeviceChangedEvent
           DeviceMovedEvent

   Argument objects for :data:`EVT_DEVICE_ADDED`, :data:`EVT_DEVICE_REMOVED`,
   :data:`EVT_DEVICE_CHANGED` and :data:`EVT_DEVICE_MOVED`.

   .. attribute:: device

      The :class:`~pyudev.Device` object that caused this event.
