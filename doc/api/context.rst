.. currentmodule:: pyudev

:class:`Context` – the central object
=====================================

.. autoclass:: Context

   .. automethod:: __init__

   .. autoattribute:: sys_path

   .. autoattribute:: device_path

   .. automethod:: list_devices

.. autoclass:: Enumerator()

   .. automethod:: match_subsystem

   .. automethod:: match_property

   .. automethod:: match_children

   .. automethod:: __iter__
