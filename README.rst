######
pyudev
######

http://pyudev.readthedocs.org

pyudev is a Python_ binding for libudev_, available under the terms fo the
`GNU LGPL 2.1`_ (see ``COPYING``).

Refer to the website_ for detailed information and API documentation.


Installation
============

The basic binding is implemented in pure Python atop of ctypes_.  The only
dependencies are udev_ and Python.pyudev supports CPython_ 2.6 or newer
(including 3.x) and PyPy_ 1.5 or newer, and is tested against udev_ 151 and
newer.  Older versions of older versions of udev_ may or may not work.

The toolkit integration modules in ``pyudev.pyqt4``, ``pyudev.pyside``,
``pyudev.glib`` and ``pyudev.wx`` require some libraries from the corresponding
toolkit.  Refer to the documentation of these modules for a more precise
description.

Installation is rather simple, just run::

   python setup.py install


Issues and Feedback
===================

There is a mailing list at pyudev@librelist.com for user questions and
development discussions around pyudev.  To subscribe to this list, just send
a mail to pyudev@librelist.com and reply to the configuration mail.  The
original mail is ditched.

Issues or enhancement proposals should be reported to the `issue tracker`_.
Thank you.


Development
===========

Development happens on GitHub_.  The complete source code is available in a
git_ repository::

   git clone --recursive git://github.com/lunaryorn/pyudev.git

Feel free to fork the repository.  Pull requests and patches are welcome!

.. _GNU LGPL 2.1: http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html
.. _Python: http://www.python.org/
.. _CPython: http://www.python.org/
.. _PyPy: http://www.pypy.org/
.. _PyQt4: http://www.riverbankcomputing.co.uk/software/pyqt/intro/
.. _udev: http://git.kernel.org/?p=linux/hotplug/udev.git
.. _libudev: http://www.kernel.org/pub/linux/utils/kernel/hotplug/libudev/
.. _website: http://pyudev.readthedocs.org
.. _ctypes: http://docs.python.org/library/ctypes.html
.. _issue tracker: http://github.com/lunaryorn/pyudev/issues
.. _GitHub: http://github.com/lunaryorn/pyudev
.. _git: http://www.git-scm.com/
