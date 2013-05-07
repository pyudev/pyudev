:mod:`pyudev.glib` – Glib/Gtk 2 integration
===========================================

.. automodule:: pyudev.glib
   :platform: Linux
   :synopsis: Glib integration

.. autoclass:: MonitorObserver

   .. attribute:: monitor

      The :class:`~pyudev.Monitor` observed by this object.

   .. attribute:: event_source

      The event source, which represents the watch on the :attr:`monitor`
      (as returned by :func:`glib.io_add_watch`), or ``None``, if
      :attr:`enabled` is ``False``.

   .. autoattribute:: enabled

   .. rubric:: Signals

   This class emits the following GObject signal:

   .. method:: device-event(observer, action, device)

      Emitted upon any device event.

      ``observer`` is the :class:`MonitorObserver`, which emitted the
      signal.  ``device`` is the :class:`~pyudev.Device`, which caused this
      event.

      Use :attr:`~pyudev.Device.action` to get the type of event.


Deprecated API
--------------

.. autoclass:: GUDevMonitorObserver

   .. attribute:: monitor

      The :class:`~pyudev.Monitor` observed by this object.

   .. attribute:: event_source

      The event source, which represents the watch on the :attr:`monitor`
      (as returned by :func:`glib.io_add_watch`), or ``None``, if
      :attr:`enabled` is ``False``.

   .. autoattribute:: enabled

   .. rubric:: Signals

   This class emits the following GObject signals:

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
