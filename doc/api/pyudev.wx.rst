:mod:`pyudev.wx` – wxPython_ integration
=====================================================

.. automodule:: pyudev.wx
   :platform: Linux
   :synopsis: wxWidgets integration


.. autoclass:: MonitorObserver

   .. attribute:: monitor

      The :class:`~pyudev.Monitor` observed by this object.

   .. autoattribute::  enabled

.. rubric:: Events

:class:`MonitorObserver` posts the following event:

.. data:: EVT_DEVICE_EVENT

   Emitted upon any device event.  Receivers get a :class:`DeviceEvent` object
   as argument.

.. class:: DeviceEvent

   Argument object for :data:`EVT_DEVICE_EVENT`.

   .. attribute:: device

      The :class:`~pyudev.Device` object that caused this event.

      Use :attr:`~pyudev.Device.action` to get the type of event.

   .. rubric:: Deprecated members

   .. attribute:: action

      A unicode string containing the action name.

      .. deprecated:: 0.17
         Will be removed in 1.0.  Use :attr:`~pyudev.Device.action` instead.


Deprecated API
--------------

.. autoclass:: WxUDevMonitorObserver

   .. attribute:: monitor

      The :class:`~pyudev.Monitor` observed by this object.

   .. autoattribute::  enabled


.. rubric:: Events

:class:`WxUDevMonitorObserver` posts the following events in addition to
:data:`EVT_DEVICE_EVENT`:

.. data:: EVT_DEVICE_ADDED

   Emitted if a :class:`~pyudev.Device` is added (e.g a USB device was
   plugged).  Receivers get a :class:`DeviceAddedEvent` object as argument.

   .. deprecated:: 0.17
      Will be removed in 1.0.

.. data:: EVT_DEVICE_REMOVED

   Emitted if a :class:`~pyudev.Device` is removed (e.g. a USB device was
   unplugged).  Receivers get a :class:`DeviceRemovedEvent` object as argument.

   .. deprecated:: 0.17
      Will be removed in 1.0.

.. data:: EVT_DEVICE_CHANGED

   Emitted if a :class:`~pyudev.Device` was somehow changed (e.g. a change of a
   property).  Receivers get a :class:`DeviceChangedEvent` object as argument.

   .. deprecated:: 0.17
      Will be removed in 1.0.

.. data:: EVT_DEVICE_MOVED

   Emitted if a :class:`~pyudev.Device` was renamed, moved or re-parented.
   Receivers get a :class:`DeviceMovedEvent` object as argument.

.. class:: DeviceAddedEvent
           DeviceRemovedEvent
           DeviceChangedEvent
           DeviceMovedEvent

   Argument objects for :data:`EVT_DEVICE_ADDED`, :data:`EVT_DEVICE_REMOVED`,
   :data:`EVT_DEVICE_CHANGED` and :data:`EVT_DEVICE_MOVED`.

   .. deprecated:: 0.17
      Will be removed in 1.0.

   .. attribute:: device

      The :class:`~pyudev.Device` object that caused this event.
