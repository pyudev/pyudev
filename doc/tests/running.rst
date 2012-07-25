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


Privileged tests
~~~~~~~~~~~~~~~~

Some tests need to execute privileged operations like loading or unloading of
kernel modules to trigger real udev events.  These tests are disabled by
default.  Refer to :mod:`~tests.plugins.privileged` for more information on how
to enable these tests and configure them properly.


Native bindings
~~~~~~~~~~~~~~~

Some tests require native bindings to other libraries. These bindings cannot be
installed by means of a ``requirements.txt`` file, but need to be build instead.
Since building these bindings is cumbersome and difficult, especially inside
virtualenvs, the ``build_bindings.py`` is provided to automate these builds.

``tox`` is configured to execute this script before running the tests, so that
tox tests will always have these bindings available.  For custom virtualenvs
however you need to perform this step manually after virtualenv creation::

   python build_bindings.py

.. warning::

   By default, builds are done under ``/tmp``, so make sure that there is enough
   space available on this filesystem, especially if it is located on ``tmpfs``.
   Use the ``--download-directory`` and ``--build-directory`` options to change
   the corresponding directories if needed.

See ``python build_bindings.py --help`` for more information.

.. _virtualenv: http://www.virtualenv.org/en/latest/index.html
.. _tox: http://tox.testrun.org/latest/
