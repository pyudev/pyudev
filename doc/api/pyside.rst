:mod:`pyudev.pyside` – PySide_ integration
==========================================

.. automodule:: pyudev.pyside
   :platform: Linux
   :synopsis: PySide integration

.. autoclass:: QUDevMonitorObserver

   .. automethod:: __init__

   .. attribute:: monitor

      The :class:`~pyudev.Monitor` observed by this object.

   .. attribute:: notifier

      The underlying :class:`QtCore.QSocketNotifier` used to watch the
      :attr:`monitor`.

   .. autoattribute:: enabled

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


.. _PySide: http://www.pyside.org
