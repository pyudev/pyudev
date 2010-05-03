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

   .. autoattribute:: dev_path

   .. automethod:: list_devices


:class:`Enumerator` – listing devices
-------------------------------------

.. autoclass:: Enumerator

   .. automethod:: match_subsystem

   .. automethod:: match_property

   .. automethod:: __iter__
