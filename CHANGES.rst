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
