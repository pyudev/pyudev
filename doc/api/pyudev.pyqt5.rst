:mod:`pyudev.pyqt5` – PyQt5_ integration
========================================

.. automodule:: pyudev.pyqt5
   :platform: Linux
   :synopsis: PyQt5 integration

.. autoclass:: MonitorObserver

   .. automethod:: __init__

   .. attribute:: monitor

      The :class:`~pyudev.Monitor` observed by this object.

   .. attribute:: notifier

      The underlying :class:`QtCore.QSocketNotifier` used to watch the
      :attr:`monitor`.

   .. autoattribute:: enabled

   .. rubric:: Signals

   This class emits the following Qt signal:

   .. method:: deviceEvent(device)

      Emitted upon any device event.

      ``device`` is the :class:`~pyudev.Device` object describing the device.

      Use :attr:`~pyudev.Device.action` to get the type of event.



.. _PyQt5: http://riverbankcomputing.co.uk/software/pyqt/intro
