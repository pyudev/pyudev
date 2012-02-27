# -*- coding: utf-8 -*-
# Copyright (C) 2010, 2011, 2012 Sebastian Wiesner <lunaryorn@googlemail.com>

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

    A binding to libudev_.

    A :class:`Context` object is required for almost any functionality in
    pyudev.  The context provides :class:`Device` enumeration with
    :meth:`Context.list_devices()`.

    Device monitoring is provided by :class:`Monitor` and
    :class:`MonitorObserver`.  With :mod:`pyudev.pyqt4`, :mod:`pyudev.pyside`,
    :mod:`pyudev.glib` and :mod:`pyudev.wx` device monitoring can be integrated
    into the event loop of various GUI toolkits.

    .. _libudev: http://www.kernel.org/pub/linux/utils/kernel/hotplug/libudev/

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)


__version__ = '0.15'
__version_info__ = tuple(map(int, __version__.split('.')))
__all__ = ['Context', 'Device']


from pyudev.device import *
from pyudev.core import *
from pyudev.monitor import *
