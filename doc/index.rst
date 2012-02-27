pyudev -- pure Python libudev_ binding
======================================

pyudev is a :doc:`LGPL licensed <licencing>`, pure Python_ binding to libudev_,
the device and hardware management and information library of Linux.

It exposes almost the complete libudev_ functionality.  You can:

* enumerate devices, filtered by specific criteria (:class:`pyudev.Context`)
* query device information, properties and attributes,
* monitor devices, both synchronously and asynchronously with background
  threads, or within the event loops of Qt (:mod:`pyudev.pyqt4`,
  :mod:`pyudev.pyside`), glib (:mod:`pyudev.glib`) and wxPython
  (:mod:`pyudev.wx`).

pyudev supports CPython_ 2 (2.6 or newer) and 3 (3.1 or newer), and PyPy_ 1.5
or newer.  It is tested against udev_ 151 or newer.  Older versions of udev_ as
found on dated Linux systems may work, but are not officially supported.


Usage
-----

Thanks to the power of libudev_, usage of pyudev is very simple.  Getting the
labels of all partitions just takes a few lines:

>>> import pyudev
>>> context = pyudev.Context()
>>> for device in context.list_devices(subsystem='block', DEVTYPE='partition'):
...     print(device.get('ID_FS_LABEL', 'unlabeled partition'))
...
boot
swap
system

The :doc:`guide` gives an introduction into the most common operations in
pyudev, a detailled reference is provided by the :doc:`api/index`.


Support
-------

.. rubric:: Mailing list

Questions about usage and development of pyudev can be posted to the mailing
list pyudev@librelist.com, which is hosted by `librelist.com`_.  To subscribe
to this list, just send a mail to pyudev@librehost.com and reply to the
confirmation mail.  To unsubscribe again, write to
pyudev-unsubscribe@librelist.com and reply to the confirmation mail.  Past
discussions and questions are available in the `list archives`_.


.. rubric:: Issues

Issues and bugs can be reported to the `issue tracker`_ on GitHub_.  Please
provide as much information as possible when reporting an issue.  Patches
addressing new or existing issues are very welcome.


.. _development:

Development
-----------

The source code is hosted on GitHub_::

   git clone --recursive git://github.com/lunaryorn/pyudev.git

Feel free to fork the repository and send pull requests or patches.  Please add
unit tests for your code, if possible.  The :doc:`testsuite documentation
<testing>` gives you an overview about the pyudev testsuite.


Contents
--------

.. toctree::

   guide
   api/index
   testing
   changes
   licencing


.. _GNU LGPL 2.1: http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html
.. _Python: http://www.python.org/
.. _CPython: http://www.python.org/
.. _PyPy: http://www.pypy.org/
.. _PyQt4: http://www.riverbankcomputing.co.uk/software/pyqt/intro/
.. _libudev: http://www.kernel.org/pub/linux/utils/kernel/hotplug/libudev/
.. _udev: http://git.kernel.org/?p=linux/hotplug/udev.git
.. _Python Package Index: http://pypi.python.org/pypi/pyudev
.. _ctypes: http://docs.python.org/library/ctypes.html
.. _librelist.com: http://librelist.com/
.. _list archives: http://librelist.com/browser/pyudev/
.. _issue tracker: https://github.com/lunaryorn/pyudev/issues
.. _GitHub: https://github.com/lunaryorn/pyudev
.. _git: http://www.git-scm.com/
.. _changesets: https://github.com/lunaryorn/pyudev/commits/master
