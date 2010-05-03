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
