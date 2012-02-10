Welcome to pyudev's documentation!
==================================

pyudev is a Python_ binding to libudev_, the hardware management library and
service found in modern linux systems.  It is available under the same
licence as the original library, which is the `GNU LGPL 2.1`_ (see
:doc:`licencing` for details).


Installation
------------

The current release is pyudev |release|, available in the `Python Package
Index`_.  Refer to the :doc:`changes` for a list of important changes since
the last release [#changes]_.

The basic binding is implemented in pure Python atop of ctypes_.  The only
dependencies are udev_ and Python.  pyudev supports CPython_ 2.6 or newer
(including 3.x) and PyPy_ 1.5 or newer, and is tested against udev_ 151 and
newer.  Older versions of older versions of udev_ may or may not work.  If
pyudev doesn't work with your udev_ version, please report an issue (see
:ref:`contribution`).

The toolkit integration modules in :mod:`pyudev.pyqt4`, :mod:`pyudev.pyside`,
:mod:`pyudev.glib` and :mod:`pyudev.wx` require some libraries from the
corresponding toolkit.  Refer to the documentation of these modules for a more
precise description.

Installation is rather simple, just run::

   pip install pyudev


Documentation
-------------

Usage of pyudev is rather simple:

>>> from pyudev import Context
>>> context = Context()
>>> for device in context.list_devices(subsystem='input', ID_INPUT_MOUSE=True):
...     if device.sys_name.startswith('event'):
...         device.parent['NAME']
...
u'"Logitech USB-PS/2 Optical Mouse"'
u'"Broadcom Corp"'
u'"PS/2 Mouse"'

Please read the :doc:`API documentation <api/index>` for detailed
information.


Feedback and Questions
----------------------

There is a mailing list at pyudev@librelist.com (hosted by `librelist.com`_)
for user questions and development discussion around pyudev.  To subscribe
to this list, just send a mail to pyudev@librelist.com and reply to the
configuration mail.  The original mail is ditched.

To unsubscribe, send a mail to pyudev-unsubscribe@librelist.com and reply to
the configuration email.

Older discussions are available in the `list archives`_.


.. _contribution:

Contribution and Development
----------------------------

Please report issues and feature requests to the `issue tracker`_
[#issues]_.  Development discussions are located on the mailing list (see
above).

Development itself happens on GitHub_.  The complete source code is
available in a git_ repository::

   git clone --recursive git://github.com/lunaryorn/pyudev.git

Feel free to fork the repository.  Pull requests and patches are welcome!  If
you indent to contribute to pyudev, you may want to read the :doc:`testsuite
documentation <testing>` to learn how to write unit tests for your code.


.. rubric:: Footnotes

.. [#changes] A detailed list of changesets_ is also available.
.. [#issues] Please assign proper labels to the issue and provide detailed
   information about the issue.  If possible, include copied and pasted
   output from the programs, or a code example demonstrating the issue.


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


.. toctree::
   :hidden:

   api/index
   licencing
   changes
   testing
