0.14 (Feb 10, 2012)
===================

- Documentation now hosted at http://pyudev.readthedocs.org (thanks to the
  readthedocs.org team for this service)
- #37: Added :class:`pyudev.wx.WxUDevMonitorObserver` for wxPython (thanks to
  Tobias Eberle)
- Added :class:`pyudev.MonitorObserver`
- Added :attr:`pyudev.glib.GUDevMonitorObserver.enabled`,
  :attr:`pyudev.pyqt4.QUDevMonitorObserver.enabled` and
  :attr:`pyudev.pyside.QUDevMonitorObserver.enabled`


0.13 (Nov 4, 2011)
==================

- #36: Added :meth:`pyudev.Monitor.set_receive_buffer_size` (thanks to Rémi
  Rérolle)
- #34: :class:`pyudev.Device.tags` returns a :class:`pyudev.Tags` object
  now
- Added :meth:`pyudev.Enumerator.match_parent`
- Added ``parent`` keyword argument to :meth:`pyudev.Enumerator.match()`
- Removed :meth:`pyudev.Enumerator.match_children` in favour of
  :meth:`pyudev.Enumerator.match_parent`
- :attr:`pyudev.Device.children` requires udev version 172 now
- #31: Added :meth:`pyudev.Enumerator.match_attribute`
- Added ``nomatch`` argument to :meth:`pyudev.Enumerator.match_subsystem` and
  :meth:`pyudev.Enumerator.match_attribute`


0.12 (Aug 31, 2011)
===================

- #32: Fixed memory leak
- #33: Fixed Python 3 support for :mod:`pyudev.glib`
- Fixed license header in :mod:`pyudev._compat`


0.11 (Jun 26, 2011)
===================

- #30: Added :attr:`pyudev.Device.sys_number`
- #29: Added :meth:`pyudev.Device.from_device_number` and
  :attr:`pyudev.Device.device_number`
- Officially support PyPy now


0.10 (Apr 20, 2011)
===================

- Added :attr:`pyudev.__version_info__`
- Added :attr:`pyudev.Device.device_type`
- :class:`pyudev.Context`, :class:`pyudev.Enumerator`, :class:`pyudev.Device`
  and :class:`pyudev.Monitor` can now directly be passed to
  :mod:`ctypes`-wrapped functions
- #24: Added :attr:`pyudev.Context.run_path`


0.9 (Mar 09, 2011)
==================

- #21: Added :meth:`pyudev.Device.find_parent`
- #22: Added :meth:`pyudev.Monitor.filter_by_tag`
- Added :attr:`pyudev.Context.log_priority` to control internal UDev logging
- Improve error reporting, if libudev is missing


0.8 (Jan 08, 2011)
==================

New features
------------

- #16: Added :meth:`pyudev.Enumerator.match` to simplify device filtering
- Added keyword arguments to :meth:`pyudev.Context.list_devices()` to simplify
  device filtering
- #19: Added :meth:`pyudev.Enumerator.match_sys_name` to match device names
- #18: Added :func:`pyudev.udev_version()` to query the version of the
  underlying udev library
- #17: Added support for initialization status, by

  - :attr:`pyudev.Device.is_initialized`,
  - :attr:`pyudev.Device.time_since_initialized` and
  - :meth:`pyudev.Enumerator.match_is_initialized`

Fixed issues
------------

- Fixed support for earlier releases of udev
- Minimum udev version is now documented for all affected attributes


0.7 (Nov 15, 2010)
==================

New features
------------

- #15: Added :mod:`pyudev.glib.GUDevMonitorObserver` for Glib and Gtk
  support


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
- added :meth:`qudev.QUDevMonitorObserver.deviceChanged` and
  :meth:`qudev.QUDevMonitorObserver.deviceMoved`


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
