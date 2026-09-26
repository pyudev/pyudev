# -*- coding: utf-8 -*-
# Copyright (C) 2010, 2011, 2012 Sebastian Wiesner <lunaryorn@gmail.com>

# This library is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation; either version 2.1 of the License, or (at your
# option) any later version.

# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
"""
pyudev
======

A binding to libudev.

The :class:`Context` provides the connection to the udev device database
and enumerates devices.  Individual devices are represented by the
:class:`Device` class.

Device monitoring is provided by :class:`Monitor` and
:class:`MonitorObserver`.  With :mod:`pyudev.pyside`,
:mod:`pyudev.glib` and :mod:`pyudev.wx` device monitoring can be integrated
into the event loop of various GUI toolkits.

.. moduleauthor::  Sebastian Wiesner  <lunaryorn@gmail.com>
"""

from pyudev._errors import DeviceNotFoundAtPathError as DeviceNotFoundAtPathError
from pyudev._errors import DeviceNotFoundByFileError as DeviceNotFoundByFileError
from pyudev._errors import DeviceNotFoundByNameError as DeviceNotFoundByNameError
from pyudev._errors import DeviceNotFoundByNumberError as DeviceNotFoundByNumberError
from pyudev._errors import DeviceNotFoundError as DeviceNotFoundError
from pyudev._errors import (
    DeviceNotFoundInEnvironmentError as DeviceNotFoundInEnvironmentError,
)
from pyudev._util import udev_version as udev_version
from pyudev.core import Context as Context
from pyudev.core import Enumerator as Enumerator
from pyudev.device import Attributes as Attributes
from pyudev.device import Device as Device
from pyudev.device import Devices as Devices
from pyudev.device import Tags as Tags
from pyudev.discover import DeviceFileHypothesis as DeviceFileHypothesis
from pyudev.discover import DeviceNameHypothesis as DeviceNameHypothesis
from pyudev.discover import DeviceNumberHypothesis as DeviceNumberHypothesis
from pyudev.discover import DevicePathHypothesis as DevicePathHypothesis
from pyudev.discover import Discovery as Discovery
from pyudev.monitor import Monitor as Monitor
from pyudev.monitor import MonitorObserver as MonitorObserver
from pyudev.version import __version__ as __version__
from pyudev.version import __version_info__ as __version_info__
