:mod:`pyudev.tests.plugins` – Testsuite plugins
===============================================

.. automodule:: pyudev.tests.plugins

The following plugins are provided and enabled:

.. autosummary::

   udev_database
   privileged
   fake_monitor

The main plugin is :mod:`~pyudev.tests.plugins.udev_database` that extracts the
real udev database using the ``udevadm`` utility and provides tests with a
sample of this database.  It also supports to restrict tests to certain udev
versions.

The other plugins only provide support for specific test cases by tuning some
hooks or adding some additional funcargs.


:mod:`~pyudev.tests.plugins.udev_database` – pytest_ plugin to access the udev device database
----------------------------------------------------------------------------------------------

.. automodule:: pyudev.tests.plugins.udev_database

.. autoclass:: DeviceDatabase()
   :members:


Test markers
------------

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

   A list of devices to use for tests as lists of device paths.


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


:mod:`~pyudev.tests.plugins.privileged` – Privileged operations
---------------------------------------------------------------

.. automodule:: pyudev.tests.plugins.privileged


Command line options
~~~~~~~~~~~~~~~~~~~~

The plugin adds the following command line options to :program:`py.test`:

.. program:: py.test

.. option:: --enable-privileged

   Enable privileged tests.  You'll need to have ``sudo`` configured correctly
   in order to run tests with this option.


:mod:`pytest` namespace
~~~~~~~~~~~~~~~~~~~~~~~

The plugin adds the following functions to the :mod:`pytest` namespace:

.. autofunction:: load_dummy

.. autofunction:: unload_dummy


:mod:`~pyudev.tests.plugins.fake_monitor` – A fake :class:`pyudev.Monitor`
--------------------------------------------------------------------------

.. automodule:: pyudev.tests.plugins.fake_monitor

.. autoclass:: FakeMonitor
   :members:


Funcargs
--------

The plugin provides the following :ref:`funcargs <funcargs>`:

.. autofunction:: pytest_funcarg__fake_monitor


.. _pytest: http://pytest.org
