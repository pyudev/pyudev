:mod:`pyudev.gi` – GObject Introspection Glib/Gtk 3 integration
===============================================================

.. automodule:: pyudev.gi
   :platform: Linux
   :synopsis: GObject introspection (GI) integration

.. autoclass:: MonitorObserver

   .. attribute:: monitor

      The :class:`~pyudev.Monitor` observed by this object.

   .. attribute:: event_source

      The event source, which represents the watch on the :attr:`monitor`
      (as returned by :func:`gi.repository.GLib.io_add_watch`), or ``None``, 
      if :attr:`enabled` is ``False``.

   .. autoattribute:: enabled

   .. rubric:: Signals

   This class emits the following GObject signal:

   .. method:: device-event(observer, action, device)

      Emitted upon any device event.

      ``observer`` is the :class:`MonitorObserver`, which emitted the
      signal.  ``device`` is the :class:`~pyudev.Device`, which caused this
      event.

      Use :attr:`~pyudev.Device.action` to get the type of event.


