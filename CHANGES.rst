0.24.4
======
Recommended development release: Fedora 41

- Add device attributes unset():
  https://github.com/pyudev/pyudev/pull/525

- Remove license classifier deprecated by PEP 639:
  https://github.com/pyudev/pyudev/pull/522

- Tidies and Maintenance:
  https://github.com/pyudev/pyudev/pull/529
  https://github.com/pyudev/pyudev/pull/528
  https://github.com/pyudev/pyudev/pull/526
  https://github.com/pyudev/pyudev/pull/524
  https://github.com/pyudev/pyudev/pull/521
  https://github.com/pyudev/pyudev/pull/520
  https://github.com/pyudev/pyudev/pull/518
  https://github.com/pyudev/pyudev/pull/512
  https://github.com/pyudev/pyudev/pull/511

0.24.3
======
Recommended development release: Fedora 40

0.24.2
======
Recommended development release: Fedora 40

- Update release infrastructure:
  https://github.com/pyudev/pyudev/pull/508

- Tidies and Maintenance:
  https://github.com/pyudev/pyudev/pull/507
  https://github.com/pyudev/pyudev/pull/506
  https://github.com/pyudev/pyudev/pull/505
  https://github.com/pyudev/pyudev/pull/503
  https://github.com/pyudev/pyudev/pull/498
  https://github.com/pyudev/pyudev/pull/497
  https://github.com/pyudev/pyudev/pull/492
  https://github.com/pyudev/pyudev/pull/491
  https://github.com/pyudev/pyudev/pull/489


0.24.1
======
Recommended development release: Fedora 37

- Add support for PySide6:
  https://github.com/pyudev/pyudev/pull/487

- Add missing 'priority' argument for GLib.to_add_watch()
  https://github.com/pyudev/pyudev/pull/479

- Tidies and Maintenance:
  https://github.com/pyudev/pyudev/pull/486
  https://github.com/pyudev/pyudev/pull/485
  https://github.com/pyudev/pyudev/pull/484
  https://github.com/pyudev/pyudev/pull/481
  https://github.com/pyudev/pyudev/pull/480
  https://github.com/pyudev/pyudev/pull/477
  https://github.com/pyudev/pyudev/pull/474


0.24.0
======
Recommended development release: Fedora 36

- Remove a bunch of Python 2 code:
  https://github.com/pyudev/pyudev/pull/468
  https://github.com/pyudev/pyudev/pull/460
  https://github.com/pyudev/pyudev/pull/455
  https://github.com/pyudev/pyudev/pull/358

- Tidies and Maintenance:
  https://github.com/pyudev/pyudev/pull/471
  https://github.com/pyudev/pyudev/pull/466
  https://github.com/pyudev/pyudev/pull/465
  https://github.com/pyudev/pyudev/pull/464
  https://github.com/pyudev/pyudev/pull/462
  https://github.com/pyudev/pyudev/pull/461
  https://github.com/pyudev/pyudev/pull/459
  https://github.com/pyudev/pyudev/pull/458
  https://github.com/pyudev/pyudev/pull/456
  https://github.com/pyudev/pyudev/pull/454
  https://github.com/pyudev/pyudev/pull/447
  https://github.com/pyudev/pyudev/pull/445


0.23.2
======
Recommended development release: Fedora 35

- New release: 0.23.2:
  https://github.com/pyudev/pyudev/pull/444

- Tidies and Maintenance:
  https://github.com/pyudev/pyudev/pull/445
  https://github.com/pyudev/pyudev/pull/443
  https://github.com/pyudev/pyudev/pull/442


0.23.1
======
Recommended development release: Fedora 34

- Update to version 0.23.1:
  https://github.com/pyudev/pyudev/pull/440

- Check for existence of _hasattr attribute in Context.__del__ method:
  https://github.com/pyudev/pyudev/issues/421
  https://github.com/pyudev/pyudev/pull/439

- Tidies and Maintenance:
  https://github.com/pyudev/pyudev/pull/438

0.23.0
======
Recommended development release: Fedora 34

- Update to version 0.23.0:
  https://github.com/pyudev/pyudev/pull/427

- Officially drop support for Python 2:
  https://github.com/pyudev/pyudev/pull/414

- Remove external mock dependency:
  https://github.com/pyudev/pyudev/pull/409

- Enable GLib unit tests:
  https://github.com/pyudev/pyudev/pull/400

- Switch to new style gi.repository.GLib imports:
  https://github.com/pyudev/pyudev/pull/399

- Tidies and Maintenance:
  https://github.com/pyudev/pyudev/pull/432
  https://github.com/pyudev/pyudev/pull/430
  https://github.com/pyudev/pyudev/pull/429
  https://github.com/pyudev/pyudev/pull/428
  https://github.com/pyudev/pyudev/pull/424
  https://github.com/pyudev/pyudev/pull/423
  https://github.com/pyudev/pyudev/pull/418
  https://github.com/pyudev/pyudev/pull/415
  https://github.com/pyudev/pyudev/pull/413


0.22.0 (Jan, 2020)
==================

- Add a six-enabled move for collections move imports:
  https://github.com/pyudev/pyudev/pull/386
- Fix any newly introduced pylint errors
- Numerous improvements or updates to the test infrastructure
- A number of test updates
- Require yapf 0.21.0 for Python formatting
- Various documentation fixes and updates


0.21.0 (July 20, 2016)
======================

- Deprecate use of Device object as mapping from udev property names to values.
- Add a Properties class and a Device.properties() method for udev properties.
- Fix places where Device object was incorrectly used in a boolean context.
- Return an empty string, not None, if the property value is an empty string.
- Exceptions re-raised from libudev calls now have a message string.
- Insert a warning about using a Device in a boolean context in docs.
- Infrastructure for vagrant tests is removed.
- Various internal refactorings.
- Extensive test improvements.
- Numerous documentation fixes.

0.20.0 (April 29, 2016)
=======================

- Remove parsing code added in previous release.
- No longer do CI for Python 2.6.
- Eliminate all wildcard imports and __all__ statements.
- No longer use deprecated Device.from_sys_path() method.
- Minor pylint induced changes.
- Documentation fixes.

0.19.0 (Feb 3, 2016)
==================

- Restore raising KeyError by Attributes.as* methods when attribute not found.
- Explicitly require six module.
- Never raise a DeviceNotFoundError when iterating over a device enumeration.
- Device.subsystem() now returns None if device has no subsystem.
- Add DeprecationWarnings to deprecated Device methods.
- Replace "/" with "!" in Device.from_name() sys_name parameter.
- Add some unstable classes for parsing some kinds of values.
- Make version info more like Python's including micro numbers and levels.
- Refactor some internal modules into subdirectories.
- Work on tests and reproducers.

0.18 (Dec 1, 2015)
===================

- DeviceNotFoundError is no longer a subtype of LookupError
- Added support for pyqt5 monitor observer
- Added discover module, which looks up a device on limited information
- Attributes class no longer extends Mapping, extends object instead
- Attributes class no longer inherits [] operator, Mapping methods
- Attributes class objects are no longer iterable
- Attributes.available_attributes property added
- Attributes.get() method, with usual semantics, defined
- Device.from_* methods are deprecated, uses Devices.from_* methods instead
- Device.from_device_file() now raises DeviceNotFoundByFileError
- Device.from_device_number() now raises DeviceNotFoundByNumberError
- Devices.from_interface_index() method added
- Devices.from_kernel_device() method added
- Numerous testing infrastructure changes

0.17 (Aug 26, 2015)
=====================

- #52: Remove global libudev object
- #57: Really start the monitor on :meth:`pyudev.Monitor.poll()`
- #60: Do not use :meth:`select.select` to avoid hitting its file descriptor
  limit
- #58: Force non-blocking IO in :class:`pyudev.Monitor` to avoid blocking on
  receiving the device
- #63: Set proper flags on pipe fds.
- #65: Handle irregular polling events properly.
- #50: Add :class:`pyudev.wx.MonitorObserver` and deprecate
  :class:`pyudev.wx.WxUDevMonitorObserver`
- #50: Add :class:`pyudev.glib.MonitorObserver` and deprecate
  :class:`pyudev.glib.GUDevMonitorObserver`
- #50: Add :class:`pyudev.pyqt4.MonitorObserver` and deprecate
  :class:`pyudev.pyqt4.QUDevMonitorObserver`
- #50: Add :class:`pyudev.pyside.MonitorObserver` and deprecate
  :class:`pyudev.pyside.QUDevMonitorObserver`
- Add a wrapper function to retry interruptible system calls.


0.16.1 (Aug 02, 2012)
=====================

- #53: Fix source distribution
- #54: Fix typo in test


0.16 (Jul 25, 2012)
===================

- Remove :meth:`pyudev.Monitor.from_socket`.
- Deprecate :meth:`pyudev.Device.traverse()` in favor of
  :attr:`pyudev.Device.ancestors`.
- #47: Deprecate :meth:`pyudev.Monitor.receive_device` in favor of
  :attr:`pyudev.Monitor.poll`.
- #47: Deprecate :attr:`pyudev.Monitor.enable_receiving` in favor of
  :attr:`pyudev.Monitor.start`.
- #47: Deprecate :attr:`pyudev.Monitor.__iter__` in favor of explicit looping or
  :class:`pyudev.MonitorObserver`.
- #49: Deprecate ``event_handler`` to :class:`pyudev.MonitorObserver` in favour
  of ``callback`` argument.
- #46: Continuously test pyudev on Travis-CI.
- Add :attr:`pyudev.Device.ancestors`.
- Add :attr:`pyudev.Device.action`.
- #10: Add :attr:`pyudev.Device.sequence_number`.
- #47: Add :meth:`pyudev.Monitor.poll`.
- #47: Add :attr:`pyudev.Monitor.started`.
- #49: Add ``callback`` argument to :class:`pyudev.Monitor`.
- :meth:`pyudev.Monitor.start` can be called repeatedly.
- #45: Get rid of 2to3
- #43: Fix test failures on Python 2.6
- Fix signature in declaration of ``udev_monitor_set_receive_buffer_size``.
- #44: Test wrapped signatures with help of ``gccxml``.
- Fix compatibility with udev 183 and newer in :class:`pyudev.Context`.
- :meth:`pyudev.MonitorObserver.stop` can be called from the observer thread.


0.15 (Mar 1, 2012)
==================

- #20: Add :meth:`~pyudev.Monitor.remove_filter()`.
- #40: Add user guide to the documentation.
- #39: Add :meth:`pyudev.Device.from_device_file()`.
- :data:`errno.EINVAL` from underlying libudev functions causes
  :exc:`~exceptions.ValueError` instead of :exc:`~exceptions.EnvironmentError`.
- :class:`pyudev.MonitorObserver` calls
  :meth:`pyudev.Monitor.enable_receiving()` when started.
- #20: :meth:`pyudev.Monitor.filter_by()` and
  :meth:`pyudev.Monitor.filter_by_tag()` can be called after
  :meth:`pyudev.Monitor.enable_receiving()`.


0.14 (Feb 10, 2012)
===================

- Host documentation at http://pyudev.readthedocs.org (thanks to the
  readthedocs.org team for this service)
- #37: Add :class:`pyudev.wx.WxUDevMonitorObserver` for wxPython (thanks to
  Tobias Eberle).
- Add :class:`pyudev.MonitorObserver`.
- Add :attr:`pyudev.glib.GUDevMonitorObserver.enabled`,
  :attr:`pyudev.pyqt4.QUDevMonitorObserver.enabled` and
  :attr:`pyudev.pyside.QUDevMonitorObserver.enabled`.


0.13 (Nov 4, 2011)
==================

- #36: Add :meth:`pyudev.Monitor.set_receive_buffer_size` (thanks to Rémi
  Rérolle).
- Add :meth:`pyudev.Enumerator.match_parent`.
- Add ``parent`` keyword argument to :meth:`pyudev.Enumerator.match()`.
- #31: Add :meth:`pyudev.Enumerator.match_attribute`.
- Add ``nomatch`` argument to :meth:`pyudev.Enumerator.match_subsystem` and
  :meth:`pyudev.Enumerator.match_attribute`.
- Remove :meth:`pyudev.Enumerator.match_children` in favour of
  :meth:`pyudev.Enumerator.match_parent`.
- #34: :class:`pyudev.Device.tags` returns a :class:`pyudev.Tags` object.
- :attr:`pyudev.Device.children` requires udev version 172 now


0.12 (Aug 31, 2011)
===================

- #32: Fix memory leak.
- #33: Fix Python 3 support for :mod:`pyudev.glib`.
- Fix license header in :mod:`pyudev._compat`.


0.11 (Jun 26, 2011)
===================

- #30: Add :attr:`pyudev.Device.sys_number`.
- #29: Add :meth:`pyudev.Device.from_device_number`
- #29: Add :attr:`pyudev.Device.device_number`.
- Support PyPy.


0.10 (Apr 20, 2011)
===================

- Add :attr:`pyudev.__version_info__`
- Add :attr:`pyudev.Device.device_type`
- :class:`pyudev.Context`, :class:`pyudev.Enumerator`, :class:`pyudev.Device`
  and :class:`pyudev.Monitor` can directly be passed to
  :mod:`ctypes`-wrapped functions.
- #24: Add :attr:`pyudev.Context.run_path`.


0.9 (Mar 09, 2011)
==================

- #21: Add :meth:`pyudev.Device.find_parent`.
- #22: Add :meth:`pyudev.Monitor.filter_by_tag`.
- Add :attr:`pyudev.Context.log_priority`.
- Improve error reporting, if libudev is missing.


0.8 (Jan 08, 2011)
==================

- #16: Add :meth:`pyudev.Enumerator.match`.
- Add keyword arguments to :meth:`pyudev.Context.list_devices()`.
- #19: Add :meth:`pyudev.Enumerator.match_sys_name`.
- #18: Add :func:`pyudev.udev_version()`.
- #17: Add :attr:`pyudev.Device.is_initialized`.
- #17: Add :attr:`pyudev.Device.time_since_initialized`.
- #17: Add :meth:`pyudev.Enumerator.match_is_initialized`
- Fix support for earlier releases of udev.
- Document minimum udev version for all affected attributes.


0.7 (Nov 15, 2010)
==================

- #15: Add :mod:`pyudev.glib.GUDevMonitorObserver`.


0.6 (Oct 03, 2010)
==================

- #8: Add :attr:`pyudev.Device.tags`.
- #8: Add :meth:`pyudev.Enumerator.match_tag`.
- #11: Add :meth:`pyudev.Device.from_environment`
- #5: Add :mod:`pyudev.pyside`
- #14: Remove apipkg_ dependency.
- #14: Require explicit import of :mod:`pyudev.pyqt4`.
- Fix licence headers in source files.

.. _apipkg: http://pypi.python.org/pypi/apipkg/


0.5 (Sep 06, 2010)
==================

- Support Python 3.
- #6: Add :attr:`pyudev.Device.attributes` (thanks to Daniel Lazzari).
- #6: Add :class:`pyudev.Attributes` (thanks to Daniel Lazzari).
- #7: :attr:`pyudev.Device.context` and :attr:`pyudev.Monitor.context` are
  part of the public API.
- #9: Add :attr:`pyudev.Device.driver`.
- #12: Add :meth:`pyudev.Device.from_name`.
- Rename :exc:`pyudev.NoSuchDeviceError` to :exc:`pyudev.DeviceNotFoundError`.
- :meth:`pyudev.Device.from_sys_path` raises
  :exc:`pyudev.DeviceNotFoundAtPathError`.
- #13: Fix :exc:`~exceptions.AttributeError` in
  :attr:`pyudev.Device.device_node`.
- Improve and extend documentation.
- Add more tests.


0.4 (Aug 23, 2010)
==================

API changes
-----------

- #3: Rename :mod:`udev` to :mod:`pyudev`.
- #3: Rename :mod:`qudev` to :mod:`pyudev.pyqt4`.
- Add :meth:`pyudev.Device.from_path`.
- :meth:`pyudev.Device.from_sys_path` raises :exc:`pyudev.NoSuchDeviceError`.
- :meth:`pyudev.Monitor.receive_device` raises
  :exc:`~exceptions.EnvironmentError`.
- ``errno``, ``strerror`` and ``filename`` attributes of
  :class:`~exceptions.EnvironmentError` exceptions have meaningful content.
- Fix :exc:`~exceptions.NameError` in :meth:`pyudev.Monitor.from_socket`
- ``subsystem`` argument to :meth:`pyudev.Monitor.filter_by` is mandatory.
- Delete underlying C objects if :class:`pyudev.Device` is garbage-collected.
- Fix broken signal emitting in :class:`pyudev.pyqt4.QUDevMonitorObserver`.


0.3 (Jul 28, 2010)
==================

- #1: Fix documentation to reflect the actual behaviour of the underlying
  API
- Raise :exc:`~exceptions.TypeError` if :class:`udev.Device` are compared with
  ``>``, ``>=``, ``<`` or ``<=``.
- Add :meth:`udev.Enumerator.match_children`.
- Add :attr:`udev.Device.children`.
- Add :meth:`qudev.QUDevMonitorObserver.deviceChanged`.
- Add :meth:`qudev.QUDevMonitorObserver.deviceMoved`.


0.2 (Jun 28, 2010)
==================

- Add :class:`udev.Monitor`.
- Add :meth:`udev.Device.asbool`.
- Add :meth:`udev.Device.asint`.
- Remove type magic in :meth:`udev.Device.__getitem__`.
- Add :mod:`qudev`.


0.1 (May 03, 2010)
==================

- Initial release.
- Add :class:`udev.Context`.
- Add :class:`udev.Device`.
- Add :class:`udev.Enumerator`.
