0.6 (Oct 03, 2010)
==================

New features
------------

- #8: Added :attr:`pyudev.Device.tags` and
  :meth:`pyudev.Enumerator.match_tag` to support device tags
- #11: Added :meth:`pyudev.Device.from_environment` to create devices from
  process environment (for use in udev rules)
- #5: Added :mod:`pyudev.pyside` for PySide support

Other changes
-------------

- #14: Removed apipkg_ dependency.  Changes the :mod:`pyudev` namespace,
  consequently ``pyudev.pyqt4.QUDevMonitorObserver`` requires prior ``import
  pyudev.pyqt4`` now.
- Fixed licence headers in source files

.. _apipkg: http://pypi.python.org/pypi/apipkg/


0.5 (Sep 06, 2010)
==================

New features
------------

- Support for Python 3
- #6: Added :attr:`pyudev.Device.attributes` and :class:`pyudev.Attributes`
  to access the attributes of a device (thanks to Daniel Lazzari for his
  efforts)
- #7: :attr:`pyudev.Device.context` and :attr:`pyudev.Monitor.context` are
  part of the public API now
- #9: Added :attr:`pyudev.Device.driver` to access the driver name
- #12: Added :meth:`pyudev.Device.from_name` to construct devices from
  subsystem and sys name

API changes
-----------

- Renamed :exc:`pyudev.NoSuchDeviceError` to
  :exc:`pyudev.DeviceNotFoundError`
- :meth:`pyudev.Device.from_sys_path` raises
  :exc:`pyudev.DeviceNotFoundAtPathError` now, which derives from
  :exc:`pyudev.DeviceNotFoundError`

Fixed issues
------------

- #13: Fixed :exc:`~exceptions.AttributeError` in
  :attr:`pyudev.Device.device_node`

Other changes
-------------

- Improved and extended documentation at some points
- Added more tests


0.4 (Aug 23, 2010)
==================

API changes
-----------

- Preferred import scheme is ``import pyudev`` now, all library classes will
  be available under the ``pyudev`` namespace then.
- #3: Renamed :mod:`udev` to :mod:`pyudev`
- #3: Renamed :mod:`qudev` to :mod:`pyudev.pyqt4`
- Added :meth:`pyudev.Device.from_path`
- :meth:`pyudev.Device.from_sys_path` raises :exc:`pyudev.NoSuchDeviceError`
  now, if no device was found at the given path.
- :meth:`pyudev.Monitor.receive_device` raises
  :exc:`~exceptions.EnvironmentError` now, if libudev did not return a
  device object, but a null pointer.
- :mod:`pyudev` interprets libudev error codes whereever possible now.
  Consequently :exc:`~exceptions.EnvironmentError` exceptions raised by
  :mod:`pyudev` classes mostly have proper ``errno``, ``strerror`` and
  ``filename`` attributes now.

Fixed issues
------------

- Fixed :exc:`~exceptions.NameError` in :meth:`pyudev.Monitor.from_socket`
- The ``subsystem`` argument to :meth:`pyudev.Monitor.filter_by` is mandatory
  now, as the underlying API requires it.
- Fixed possible memory leak:  :class:`pyudev.Device` objects now delete the
  underlying libudev object, when garbage-collected
- Fixed broken signal emitting in :class:`pyudev.pyqt4.QUDevMonitorObserver`


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
