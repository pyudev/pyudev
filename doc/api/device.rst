.. currentmodule:: pyudev

:class:`Device` – accessing device information
==============================================

.. autoclass:: Device()

   .. automethod:: from_path

   .. automethod:: from_sys_path

   .. automethod:: from_name

   .. automethod:: from_environment

   .. attribute:: context

      The :class:`Context` to which this device is bound.

      .. versionadded:: 0.5

   .. autoattribute:: sys_path

   .. autoattribute:: sys_name

   .. autoattribute:: device_path

   .. autoattribute:: subsystem

   .. autoattribute:: driver

   .. autoattribute:: device_node

   .. autoattribute:: device_links

   .. autoattribute:: attributes

   .. autoattribute:: tags

   .. autoattribute:: parent

   .. autoattribute:: children

   .. automethod:: traverse

   .. automethod:: __iter__

   .. automethod:: __len__

   .. automethod:: __getitem__

   .. automethod:: asint

   .. automethod:: asbool

.. autoclass:: Attributes()

   .. attribute:: device

      The :class:`Device` to which these attributes belong.

   .. automethod:: __iter__

   .. automethod:: __len__

   .. automethod:: __getitem__

   .. automethod:: asstring

   .. automethod:: asint

   .. automethod:: asbool


Exceptions
----------

.. autoclass:: DeviceNotFoundError

.. autoclass:: DeviceNotFoundAtPathError
   :members:

.. autoclass:: DeviceNotFoundByNameError
   :members:

.. autoclass:: DeviceNotFoundInEnvironmentError
   :members:
