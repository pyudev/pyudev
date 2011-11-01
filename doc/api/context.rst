.. currentmodule:: pyudev

:class:`Context` – the central object
=====================================

.. autoclass:: Context

   .. automethod:: __init__

   .. autoattribute:: sys_path

   .. autoattribute:: device_path

   .. autoattribute:: run_path

   .. autoattribute:: log_priority

   .. automethod:: list_devices

.. autoclass:: Enumerator()

   .. automethod:: match

   .. automethod:: match_subsystem

   .. automethod:: match_sys_name

   .. automethod:: match_property

   .. automethod:: match_attribute

   .. automethod:: match_tag

   .. automethod:: match_parent

   .. automethod:: match_is_initialized

   .. automethod:: __iter__
