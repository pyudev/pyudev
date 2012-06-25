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


.. _support:

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

Please report issues and bugs to the `issue tracker`_, but respect the following
guidelines:

- Check that the issue has not already been reported.
- Check that the issue is not already fixed in the ``master`` branch.
- Open issues with clear title and a detailed description in grammatically
  correct, complete sentences.
- Include the Python version and the udev version (see ``udevadm --version``) in
  the description of your issue.


.. _development:

Development
-----------

The source code is hosted on GitHub_::

   git clone git://github.com/lunaryorn/pyudev.git

Please fork the repository and send pull requests with your fixes or new
features, but respect the following guidelines:

- Read `how to properly contribute to open source projects on GitHub
  <http://gun.io/blog/how-to-github-fork-branch-and-pull-request/>`_.
- Use a topic branch to easily amend a pull request later, if necessary.
- Write `good commit messages
  <http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html>`_.
- Squash commits on the topic branch before opening a pull request.
- Respect :pep:`8` (use pep8_ to check your coding style compliance).
- Add unit tests if possible (refer to the
  :doc:`testsuite documentation <tests/index>`).
- Add API documentation in docstrings.
- Do not break the API of existing code in your changes.
- Open a `pull request <https://help.github.com/articles/using-pull-requests>`_
  that relates to but one subject with a clear title and description in
  grammatically correct, complete sentences.


Contents
--------

.. toctree::

   guide
   api/index
   tests/index
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
.. _pep8: http://pypi.python.org/pypi/pep8/
