:mod:`plugins` – Testsuite plugins
==================================

.. automodule:: plugins

The following plugins are provided and enabled:

.. autosummary::

   .fake_monitor
   .mock_libudev
   .travis


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
