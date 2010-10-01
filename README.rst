######
pyudev
######

http://packages.python.org/pyudev

pyudev is a Python_ and PyQt4_ binding for libudev_, available under the
terms fo the `GNU LGPL 2.1`_ (see ``COPYING``).

Refer to the website_ for detailed information and API documentation.


Installation
============

The binding is implemented in pure Python atop of ctypes_, contains no
native code and has no dependencies.  The only requirement is Python 2.6 or
newer, Python 3 is supported as well.

Installation is rather simple, just run::

   python setup.py install

Additionally libudev must be available at runtime in order to ``import
pyudev``.


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

   git clone git://github.com/lunaryorn/pyudev.git

Feel free to fork the repository.  Pull requests and patches are welcome!

.. _`GNU LGPL 2.1`: http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html
.. _Python: http://www.python.org/
.. _PyQt4: http://www.riverbankcomputing.co.uk/software/pyqt/intro/
.. _libudev: http://www.kernel.org/pub/linux/utils/kernel/hotplug/udev.html
.. _website: http://packages.python.org/pyudev
.. _ctypes: http://docs.python.org/library/ctypes.html
.. _`issue tracker`: http://github.com/lunaryorn/pyudev/issues
.. _GitHub: http://github.com/lunaryorn/pyudev
.. _git: http://www.git-scm.com/
