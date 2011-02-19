.. currentmodule:: pyudev

:class:`Monitor` – monitor devices
----------------------------------

.. autoclass:: Monitor()

   .. automethod:: from_netlink

   .. automethod:: from_socket

   .. attribute:: context

      The :class:`Context` to which this monitor is bound.

      .. versionadded:: 0.5

   .. automethod:: fileno

   .. automethod:: filter_by

   .. automethod:: filter_by_tag

   .. automethod:: enable_receiving

   .. method:: start

      Alias for :meth:`enable_receiving`

   .. automethod:: receive_device

   .. automethod:: __iter__
