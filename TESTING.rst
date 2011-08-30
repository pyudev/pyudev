======================
 Unittests for pyudev
======================

Unittests for pyudev are contained in the sub-directory ``tests``.  The unit
tests are written using the pytest_ framework.

Using tox_
==========

A ``tox.ini`` file is provided to run all tests with tox_.  tox_ automatically
creates virtualenvs, installs the necessary modules and bindings and runs the
test command.

Assuming that tox_ is installed, just run the following command to test pyudev
against Python 2.7, Python 3.2 and PyPy::

   tox -e py27,py32,pypy

You can pass arbitrary pytest_ arguments after two dashes ``--``::

   tox -e py27,py32,pypy -- -k device

Run the following command to get an overview over all options::

   tox -e py27 -- --help


Manual execution
================

You can also create your own virtualenv to test pyudev.  In this case you need
to install the dependencies manually.

Virtualenv setup
----------------

``virtualenv`` setup is easy::

   virtualenv pyudev
   . pyudev/bin/activate.sh
   export LD_LIBRARY_PATH=${VIRTUALENV}/lib

The last line is important if you intend to build the native bindings for tests
(see next section).  Some of these depend on helper libraries installed to this
directory, which can only be loaded if the library path includes the ``lib/``
directory of the virtualenv.  Otherwise you will get ``ImportError``\ s,
because these libraries cannot be loaded.


Dependencies
------------

The pure Python dependencies are contained in the pip_ requirements file
``tests/requirements.txt``, just install them with ``pip``::

   pip install -r tests/requirements.txt

These dependencies are mandatory, the testsuite will not work without these
modules.

Some tests additionally require modules from native bindings.  If these are not
available, the corresponding tests are skipped.  A ``Makefile`` is provided to
build and install all required bindings, just run::

   make -C tests bindings

The bindings are automatically installed into the currently active
``virtualenv``, or into system Python, if no ``virtualenv`` is active.

.. note::

   Dependencies of these bindings like Qt or glib are *not* build.  These are
   assumed to be installed on your system.


Test running
------------

Once the dependencies are installed, just use ``py.test`` to run all tests::

   py.test


Notes
=====

Device samples
--------------

Most of the tests run against the real udev device database of the system.  The
device database is extracted from the output of the ``udevadm`` utility.  By
default the tests use only a small random sample of the whole database, because
a system typically has some hundred or thousand devices.  The default size of
this sample is ten devices, you can however choose another sample size::

   py.test --device-sample-size 100

You can also run the tests with a specific device, or with all devices::

   py.test --device /devices/virtual/tty/tty1
   py.test --all-devices

Be sure to not include the ``/sys`` prefix in the argument of ``--device``.


Privileged tests
----------------

Some tests require root privileges to load and unload modules and so trigger
udev events.  By default these tests are skipped.  You can run these tests by
passing ``--allow-privileges`` to the test runner::

   py.test --allow-privileges

Privileges are accquired through ``sudo``, thus you will see password prompts
during test execution.  The executed commands are ``modprobe dummy`` and
``modprobe -r dummy``.


.. _pip: http://pip-installer.org
.. _pytest: http://pytest.org
.. _tox: http://tox.testrun.org
