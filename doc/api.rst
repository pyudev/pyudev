:mod:`udev` – pyudev API
========================

.. automodule:: udev
   :platform: Linux
   :synopsis: libudev bindings


:class:`Context` – the central object
-------------------------------------

.. autoclass:: Context

   .. automethod:: __init__

   .. autoattribute:: sys_path

   .. autoattribute:: device_path

   .. automethod:: list_devices


:class:`Enumerator` – listing devices
-------------------------------------

.. autoclass:: Enumerator

   .. automethod:: match_subsystem

   .. automethod:: match_property

   .. automethod:: __iter__


:class:`Device` – accessing device information
----------------------------------------------

.. autoclass:: Device

   .. automethod:: from_sys_path

   .. autoattribute:: sys_path

   .. autoattribute:: sys_name

   .. autoattribute:: device_path

   .. autoattribute:: subsystem

   .. autoattribute:: device_node

   .. autoattribute:: device_links

   .. autoattribute:: parent

   .. automethod:: traverse

   .. automethod:: __iter__

   .. automethod:: __len__

   .. automethod:: __getitem__

   .. automethod:: asint

   .. automethod:: asbool


:class:`Monitor` – monitor devices
----------------------------------

.. autoclass:: Monitor

   .. automethod:: from_netlink

   .. automethod:: from_socket

   .. automethod:: fileno

   .. automethod:: filter_by

   .. automethod:: enable_receiving

   .. method:: start

      Alias for :meth:`enable_receiving`

   .. automethod:: receive_device

   .. automethod:: __iter__
