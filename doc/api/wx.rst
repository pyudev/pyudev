:mod:`pyudev.wx` – wxPython_ integration
=====================================================

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


.. _wxPython: http://www.wxpython.org
