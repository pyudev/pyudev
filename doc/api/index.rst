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

   This attribute is mainly intended for display purposes, use
   :data:`__version_info__` to check the version of :mod:`pyudev` in source
   code.

.. data:: __version_info__

   The version of :mod:`pyudev` as tuple of integers.  This tuple contains a
   major and a minor number, and optionally a revision number in the form
   ``(major, minor, revision)``.  As said, the ``revision`` component is
   optional and may not be present.

   .. versionadded:: 0.10

.. autofunction:: udev_version()
