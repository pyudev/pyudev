Toolkit integration
===================

:mod:`pyudev.pyqt4` – Py4Qt integration
---------------------------------------

.. module:: pyudev.pyqt4
   :platform: Linux
   :synopsis: PyQt4 binding to :mod:`pyudev`

If you already have an existing context or monitor object and simply want to
plug the monitoring into the Qt event loop, use
:class:`QUDevMonitorObserver`:

.. autoclass:: QUDevMonitorObserver
   :show-inheritance:

   .. automethod:: __init__

   .. pyqt4:signal:: deviceEvent(action, device)

      Emitted upon any device event.  ``action`` is a unicode string
      containing the action name, and ``device`` is the
      :class:`~pyudev.Device` object describing the device.

      The arguments of this signal are basically the return value of
      :meth:`~pyudev.Monitor.receive_device`

   .. pyqt4:signal:: deviceAdded(device)

      Emitted if a :class:`~pyudev.Device` is added (e.g a USB device was
      plugged).

   .. pyqt4:signal:: deviceRemoved(device)

      Emitted if a :class:`~pyudev.Device` is removed (e.g. a USB device was
      unplugged).

   .. pyqt4:signal:: deviceChanged(device)

      Emitted if a :class:`~pyudev.Device` was somehow changed (e.g. a
      change of a property)

   .. pyqt4:signal:: deviceMoved(device)

      Emitted if a :class:`~pyudev.Device` was renamed, moved or
      re-parented.
