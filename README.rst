######
pyudev
######

http://packages.python.org/pyudev

pyudev is a Python_ binding for libudev_, available under the terms fo the
`GNU LGPL 2.1`_ (see ``COPYING``).

Refer to the website_ for detailed information and API documentation.


Installation
============

The binding is implemented in pure Python atop of ctypes_ and contains no
native code.  Therefore, no compiler is required for installation, simply
run::

   python setup.py install

To load the module, libudev must be available.


Issues and Feedback
===================

Please report issues, proposals or enhancements to the `issue tracker`_.


Development
===========

Development happens on GitHub_.  The complete source code is available in a
git_ repository::

   git clone git://github.com/lunaryorn/pyudev.git

Feel free to fork the repository.  Pull requests and patches are welcome!

.. _`GNU LGPL 2.1`: http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html
.. _Python: http://www.python.org/
.. _libudev: http://www.kernel.org/pub/linux/utils/kernel/hotplug/udev.html
.. _website: http://packages.python.org/pyudev
.. _ctypes: http://docs.python.org/library/ctypes.html
.. _`issue tracker`: http://github.com/lunaryorn/pyudev/issues
.. _GitHub: http://github.com/lunaryorn/pyudev
.. _git: http://www.git-scm.com/

