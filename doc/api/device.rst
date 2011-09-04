.. currentmodule:: pyudev

:class:`Device` – accessing device information
==============================================

.. autoclass:: Device()

   .. rubric:: Construction of device objects

   .. automethod:: from_path

   .. automethod:: from_sys_path

   .. automethod:: from_name

   .. automethod:: from_device_number

   .. automethod:: from_environment

   .. rubric:: General attributes

   .. attribute:: context

      The :class:`Context` to which this device is bound.

      .. versionadded:: 0.5

   .. autoattribute:: sys_path

   .. autoattribute:: sys_name

   .. autoattribute:: sys_number

   .. autoattribute:: device_path

   .. autoattribute:: tags

   .. rubric:: Device driver and subsystem

   .. autoattribute:: subsystem

   .. autoattribute:: driver

   .. autoattribute:: device_type

   .. rubric:: Device nodes

   .. autoattribute:: device_node

   .. autoattribute:: device_number

   .. autoattribute:: device_links

   .. rubric:: Device initialization time

   .. autoattribute:: is_initialized

   .. autoattribute:: time_since_initialized

   .. rubric:: Device hierarchy

   .. autoattribute:: parent

   .. autoattribute:: children

   .. automethod:: traverse

   .. automethod:: find_parent

   .. rubric:: Device properties

   .. automethod:: __iter__

   .. automethod:: __len__

   .. automethod:: __getitem__

   .. automethod:: asint

   .. automethod:: asbool

   .. rubric:: Sysfs attributes

   .. autoattribute:: attributes

.. autoclass:: Attributes()

   .. attribute:: device

      The :class:`Device` to which these attributes belong.

   .. automethod:: __iter__

   .. automethod:: __len__

   .. automethod:: __getitem__

   .. automethod:: asstring

   .. automethod:: asint

   .. automethod:: asbool

.. autoclass:: Tags()

   .. automethod:: __iter__

   .. automethod:: __contains__


Exceptions
----------

.. autoclass:: DeviceNotFoundError

.. autoclass:: DeviceNotFoundAtPathError
   :members:

.. autoclass:: DeviceNotFoundByNameError
   :members:

.. autoclass:: DeviceNotFoundByNumberError
   :members:

.. autoclass:: DeviceNotFoundInEnvironmentError
   :members:
