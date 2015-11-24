:mod:`plugins` – Testsuite plugins
==================================

.. automodule:: plugins

The following plugins are provided and enabled:

.. autosummary::

   .privileged
   .fake_monitor
   .mock_libudev
   .travis

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

.. autofunction:: fake_monitor


:mod:`~plugins.mock_libudev` – Mock calls to libudev
----------------------------------------------------

.. automodule:: plugins.mock_libudev

.. autofunction:: libudev_list(function, items)


:mod:`~plugins.travis` – Support for Travis CI
----------------------------------------------

.. automodule:: plugins.travis


Test markers
~~~~~~~~~~~~

.. attribute:: pytest.mark.not_on_travis

   Do not run the decorated test on Travis CI::

      @pytest.mark.not_on_travis
      def test_foo():
          assert True

   ``test_foo`` will not be run on Travis CI.


:mod:`pytest` namespace
~~~~~~~~~~~~~~~~~~~~~~~

The plugin adds the following functions to the :mod:`pytest` namespace:

.. autofunction:: is_on_travis_ci


.. _pytest: http://pytest.org
