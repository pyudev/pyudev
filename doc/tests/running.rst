Test running
============

Automatic execution using tox_
------------------------------

The recommended way to run all tests is to use tox_.  This tool automatically
creates virtual environments with virtualenv_ with all requirements installed
and runs the tests.

Assuming that tox_ is installed, the following command will run the pyudev
tests against Python 2.7, Python 3.2 and PyPy::

   tox -e py27,py32,pypy

You can pass arbitrary :program:`py.test` arguments after two dashes ``--``::

   tox -e py27,py32,pypy -- --enable-privileged


Manual execution
----------------

You can also run tests manually with :program:`py.test`.  It is recommended to
setup a separate virtual environment for this purpose::

   $ virtualenv pyudv
   $ . pyudev/bin/activate.sh

Then use the provided :file:`requirements.txt` file to install the necessary
modules into this virtual environment by running the following command from the
root of the pyudev source tree::

   $ pip install -r requirements.txt


.. _virtualenv: http://www.virtualenv.org/en/latest/index.html
.. _tox: http://tox.testrun.org/latest/
