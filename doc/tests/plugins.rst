:mod:`plugins` – Testsuite plugins
==================================

.. automodule:: plugins

The following plugins are provided and enabled:

.. autosummary::

   udev_database
   privileged
   fake_monitor
   mock_libudev
   libudev

The main plugin is :mod:`~plugins.udev_database` that extracts the
real udev database using the ``udevadm`` utility and provides tests with a
sample of this database.  It also supports to restrict tests to certain udev
versions.

The other plugins only provide support for specific test cases by tuning some
hooks or adding some additional funcargs.


:mod:`~plugins.udev_database` – pytest_ plugin to access the udev device database
---------------------------------------------------------------------------------

.. automodule:: plugins.udev_database

.. autoclass:: DeviceDatabase()
   :members:

.. autoclass:: DeviceData()
   :members:

   .. attribute:: device_path

      The path of the device without the ``sysfs`` mountpoint.


Test markers
~~~~~~~~~~~~

.. function:: pytest.mark.udev_version(version_spec)

   Specify the udev version requirement for a test::

      @pytest.mark.udev_version('>= 180')
      def test_foo():
          assert True

   ``test_foo`` will only be run, if the udev version is greater or equal than
   180.  Otherwise the test is skipped.

   ``version_spec`` is a string specifying the udev version requirement.  If
   the requirement is not met, the test is skipped.


Configuration values
~~~~~~~~~~~~~~~~~~~~

The plugin attaches the following attributes to :data:`pytest.config`:

.. attribute:: pytest.config.udev_version

   The udev version as integer.

.. attribute:: pytest.config.udev_database

   The whole udev device database as :class:`DeviceDatabase` object.

.. attribute:: pytest.config.udev_device_sample

   A list of devices to use for tests as list of :class:`DeviceData` objects,
   an excerpt of :attr:`pytest.config.udev_database`.


Funcargs
~~~~~~~~

The plugin provides the following :ref:`funcargs <funcargs>`:

.. autofunction:: pytest_funcarg__udev_database


Command line options
~~~~~~~~~~~~~~~~~~~~

The plugin adds the following command line options to :program:`py.test`:

.. program:: py.test

.. option:: --all-devices

   Run device tests against *all* devices in the database.  By default, only a
   random sample of devices are being tested against.

   .. warning::

      Tests may take a very long time with this option.

.. option:: --device DEVICE

   Run device tests against a specific device only.  ``DEVICE`` is the device
   path *without* the sysfs mountpoint.

.. option:: --device-sample-size N

   The size of the random sample.  Defaults to 10.


:mod:`~plugins.privileged` – Privileged operations
--------------------------------------------------

.. automodule:: plugins.privileged


Command line options
~~~~~~~~~~~~~~~~~~~~

The plugin adds the following command line options to :program:`py.test`:

.. program:: py.test

.. option:: --enable-privileged

   Enable privileged tests.  You'll need to have :program:`sudo` configured
   correctly in order to run tests with this option.


Configuration
~~~~~~~~~~~~~

In order to execute these tests without failure, you need to configure :program:`sudo`
to allow the user that executes the test to run the following commands:

- ``modprobe dummy``
- ``modprobe -r dummy``

To do so, create a file ``/etc/sudoers.d/20pyudev-tests`` with the following
content::

   me ALL = (root) NOPASSWD: /sbin/modprobe dummy, /sbin/modprobe -r dummy

Replace ``me`` with your actual user name.  ``NOPASSWD:`` tells :program:`sudo`
not to ask for a password when executing these commands.  This is simply for
the sake of convenience and to allow unattended test execution.  Remove this
word if you want to be asked for a password.

Make sure to change the owner and group to ``root:root`` and the permissions of
this file to ``440`` afterwards, other :program:`sudo` will refuse to load the
file.  Also check the file with :program:`visudo` to prevent syntactic errors::

   $ chown root:root /etc/sudoers.d/20pyudev-tests
   $ chmod 440 /etc/sudoers.d/20pyudev-tests
   $ visudo -c -f /etc/sudoers.d/20pyudev-tests



:mod:`pytest` namespace
~~~~~~~~~~~~~~~~~~~~~~~

The plugin adds the following functions to the :mod:`pytest` namespace:

.. autofunction:: load_dummy

.. autofunction:: unload_dummy


:mod:`~plugins.fake_monitor` – A fake :class:`Monitor`
------------------------------------------------------

.. automodule:: plugins.fake_monitor

.. autoclass:: FakeMonitor
   :members:


Funcargs
~~~~~~~~

The plugin provides the following :ref:`funcargs <funcargs>`:

.. autofunction:: pytest_funcarg__fake_monitor


:mod:`~plugins.mock_libudev` – Mock calls to libudev
----------------------------------------------------

.. automodule:: plugins.mock_libudev

.. autofunction:: calls_to_libudev(function_calls)

.. autofunction:: libudev_list(function, items)


:mod:`~plugins.libudev` – Parse ``libudev.h``
---------------------------------------------

.. automodule:: plugins.libudev


Configuration values
~~~~~~~~~~~~~~~~~~~~

This plugin attaches the following attribute to :data:`pytest.config`:

.. attribute:: libudev_functions

   All libudev functions as list of :class:`Function` objects.


Funcargs
~~~~~~~~

This plugin provides the the following :ref:`funcarg <funcargs>`:

.. autofunction:: pytest_funcarg__libudev_function


Types
~~~~~

.. autoclass:: GCCXMLParser
   :members:

.. autoclass:: Unit
   :members:

.. rubric:: Symbol classes

.. class:: Function

   A function.

   .. attribute:: name

      The function name as string

   .. attribute:: arguments

      A tuple providing with the argument types of this function

   .. attribute:: return_type

      The return type of this function

.. class:: Struct

   A structure.

   .. attribute:: name

      The struct name as string

.. class:: FundamentalType

   A fundamental type.

   .. attribute:: name

      The type name as string

.. class:: CvQualifiedType

   A constant-qualified type.

   .. attribute:: type

      The underlying type

.. class:: PointerType

   A pointer type.

   .. attribute:: type

      The underyling type


.. _pytest: http://pytest.org
