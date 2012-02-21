######
pyudev
######

http://pyudev.readthedocs.org

pyudev is a LGPL_ licensed, pure Python_ binding for libudev_, the device and
hardware management and information library for Linux.  It supports almost all
libudev_ functionality, you can enumerate devices, query device properties and
attributes or monitor devices, including asynchronous monitoring with threads,
or within the event loops of Qt, Glib or wxPython.

The binding supports CPython_ 2 (2.6 or newer) and 3 (3.1 or newer), and PyPy_
1.5 or newer.  It is tested against udev 151 or newer, earlier versions of udev
as found on dated Linux systems may work, but are not officially supported.

The website_ provides detailed information and complete API documentation.


Support, issues and source code
===============================

A mailinig list is available at pyudev@librelist.com for questions and
discussions about pyudev usage and development.  To subscribe to this list,
just send a mail to pyudev@librelist.com and reply to the confirmation mail.

Bugs and issues can be reported to the issue `issue tracker`_ on GitHub_.  The
source code is located in a git_ repository on GitHub_, too::

   git clone --recursive git://github.com/lunaryorn/pyudev.git

Feel free to fork the repository.  Pull requests and patches are welcome!


.. _LGPL: http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html
.. _Python: http://www.python.org/
.. _CPython: http://www.python.org/
.. _PyPy: http://www.pypy.org/
.. _libudev: http://www.kernel.org/pub/linux/utils/kernel/hotplug/libudev/
.. _website: http://pyudev.readthedocs.org
.. _issue tracker: http://github.com/lunaryorn/pyudev/issues
.. _GitHub: http://github.com/lunaryorn/pyudev
.. _git: http://www.git-scm.com/
