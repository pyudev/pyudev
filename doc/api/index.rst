:py:mod:`pyudev` – pyudev API
=============================

.. automodule:: pyudev
   :platform: Linux
   :synopsis: libudev bindings


Module contents
---------------

.. toctree::

   context
   device
   monitor
   toolkit


Other attributes
----------------

.. data:: __version__

   The version of :mod:`pyudev` as string.  This string contains a major and a
   minor version number, and optionally a revision in the form
   ``major.minor.revision``.  As said, the ``revision`` part is optional and
   may not be present.

   This attribute is mainly intended for display purposes, but should you
   really need to check the version of :mod:`pyudev`, you can use something
   like this::

      version = tuple(map(int, pyudev.__version__.split('.')[:2]))
      assert version >= (0, 8)
