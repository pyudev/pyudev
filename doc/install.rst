Installation
============

Python versions and implementations
-----------------------------------

pyudev supports CPython 3 and compatible versions of PyPy.


Dependencies
------------

pyudev needs libudev 151 and newer, earlier versions of libudev as found on
dated Linux systems may work, but are not tested and not officially supported.
It is written in pure Python based on :mod:`ctypes`, so no compilers or headers
are required for installation.

To use any of the toolkit integration modules. the corresponding toolkit must be
available, but no toolkit is required during installation.


Installation from Cheeseshop
----------------------------

Install pyudev from the Cheeseshop_ with pip_::

   pip install pyudev


Installation from source code
-----------------------------

Close the public repository::

   git clone https://github.com/lunaryorn/pyudev.git

Or download `tarball <https://github.com/lunaryorn/pyudev/tarball/master>`_::

   curl -OL https://github.com/lunaryorn/pyudev/tarball/master

Then install pyudev from the source code tree::

   python setup.py install


.. _Cheeseshop: http://pypi.python.org/pypi/pyudev
.. _pip: http://www.pip-installer.org/
