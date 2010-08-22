0.4 (in development)
====================

API changes
-----------

- :meth:`udev.Device.from_sys_path` raises :exc:`udev.NoSuchDeviceError` now,
  if no device was found at the given path.
- :meth:`udev.Monitor.receive_device` raises
  :exc:`~exceptions.EnvironmentError` now, if libudev did not return a
  device object, but a null pointer.
- :mod:`udev` interprets libudev error codes whereever possible now.
  Consequently :exc:`~exceptions.EnvironmentError` exceptions raised by
  :mod:`udev` classes mostly have proper ``errno``, ``strerror`` and
  ``filename`` attributes now.

Fixed issues
------------

- Fixed :exc:`~exceptions.NameError` in :meth:`udev.Monitor.from_socket`
- The ``subsystem`` argument to :meth:`udev.Monitor.filter_by` is mandatory
  now, as the underlying API requires it.
- Fixed possible memory leak:  :class:`udev.Device` now delete the
  underlying libudev object, when garbage-collected
- Fixed broken signal emitting in :class:`qudev.QUDevMonitorObserver`


0.3 (Jul 28, 2010)
==================

- #1: Fixed documentation to reflect the actual behaviour of the underlying
  API
- ``>``, ``>=``, ``<`` or ``<=`` raise :exc:`~exceptions.TypeError` now, if
  used on :class:`udev.Device` objects.
- added :meth:`udev.Enumerator.match_children` and
  :attr:`udev.Device.children` to list direct children of a device
- added :pyqt4:signal:`qudev.QUDevMonitorObserver.deviceChanged` and
  :pyqt4:signal:`qudev.QUDevMonitorObserver.deviceMoved`


0.2 (Jun 28, 2010)
==================

- added :class:`udev.Monitor` to support event monitoring
- added :meth:`udev.Device.asbool` and :meth:`udev.Device.asint`
- removed type magic in :meth:`udev.Device.__getitem__`
- added :mod:`qudev` to for PyQt4 integration


0.1 (May 03, 2010)
==================

- Initial release
- added :class:`udev.Context`
- added :class:`udev.Device`
- added :class:`udev.Enumerator`
