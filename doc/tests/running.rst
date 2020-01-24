Test running
============


Direct testing using tox_
-------------------------

If you are on a Linux system run all tests with tox_.  This tool automatically
creates virtualenvs (see virtualenv_), installs all packages required by the
test suite, and runs the tests.

Run all pyudev tests against Python 2.7, Python 3.2 and PyPy::

   tox -e py27,py32,pypy

Pass any arguments you want to :program:`py.test` after two dashes ``--``::

   tox -e py27,py32,pypy -- --<argument>


Notes
-----

Device samples
~~~~~~~~~~~~~~

Many pyudev tests run against the real device database of the system the tests
are executed on.  As testing against the whole database takes a long time,
tests are run against a random sample by default.  With the command line
options provided by :mod:`~tests.plugins.udev_database` you can configure the
size of this sample, or run the tests against a single device or the whole
database.
