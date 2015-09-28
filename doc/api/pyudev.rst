:mod:`pyudev` - libudev binding
===============================

.. automodule:: pyudev
   :platform: Linux
   :synopsis: libudev bindings

.. autosummary::
   :nosignatures:

   Context
   Device
   Devices
   Monitor
   MonitorObserver


Version information
-------------------

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


:class:`Context` – UDev database context
----------------------------------------

.. autoclass:: Context

   .. automethod:: __init__

   .. autoattribute:: sys_path

   .. autoattribute:: device_path

   .. autoattribute:: run_path

   .. autoattribute:: log_priority

   .. automethod:: list_devices


:class:`Enumerator` – device enumeration and filtering
------------------------------------------------------

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


:class:`Devices` – constructing `Device` objects
------------------------------------------------

.. autoclass:: Devices()

   .. rubric:: Construction of device objects

   .. automethod:: from_path

   .. automethod:: from_sys_path

   .. automethod:: from_name

   .. automethod:: from_device_number

   .. automethod:: from_device_file

   .. automethod:: from_environment

   .. automethod:: METHODS


:class:`Device` – accessing device information
----------------------------------------------

.. autoclass:: Device()

   .. rubric:: Construction of device objects

   .. automethod:: from_path

   .. automethod:: from_sys_path

   .. automethod:: from_name

   .. automethod:: from_device_number

   .. automethod:: from_device_file

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

   .. autoattribute:: ancestors

   .. autoattribute:: children

   .. automethod:: find_parent

   .. rubric:: Device events

   .. autoattribute:: action

   .. autoattribute:: sequence_number

   .. rubric:: Device properties

   .. automethod:: __iter__

   .. automethod:: __len__

   .. automethod:: __getitem__

   .. automethod:: asint

   .. automethod:: asbool

   .. rubric:: Sysfs attributes

   .. autoattribute:: attributes

   .. rubric:: Deprecated members

   .. automethod:: traverse

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


:class:`Device` exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: DeviceNotFoundError

.. autoclass:: DeviceNotFoundAtPathError
   :members:

.. autoclass:: DeviceNotFoundByNameError
   :members:

.. autoclass:: DeviceNotFoundByNumberError
   :members:

.. autoclass:: DeviceNotFoundInEnvironmentError
   :members:


:class:`Monitor` – device monitoring
------------------------------------

.. autoclass:: Monitor()

   .. automethod:: from_netlink

   .. attribute:: context

      The :class:`Context` to which this monitor is bound.

      .. versionadded:: 0.5

   .. autoattribute:: started

   .. automethod:: fileno

   .. automethod:: filter_by

   .. automethod:: filter_by_tag

   .. automethod:: remove_filter

   .. automethod:: start

   .. automethod:: set_receive_buffer_size

   .. automethod:: poll

   .. rubric:: Deprecated members

   .. automethod:: enable_receiving

   .. automethod:: receive_device

   .. automethod:: __iter__


:class:`MonitorObserver` – asynchronous device monitoring
---------------------------------------------------------

.. autoclass:: MonitorObserver

   .. attribute:: monitor

      Get the :class:`Monitor` observer by this object.

   .. automethod:: __init__

   .. automethod:: send_stop

   .. automethod:: stop
