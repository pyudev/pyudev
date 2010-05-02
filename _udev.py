# Copyright (C) 2010 Sebastian Wiesner <lunaryorn@googlemail.com>

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
    _udev
    =====

    Wrapper types for libudev.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""


import ctypes
from ctypes.util import find_library


class udev(ctypes.Structure):
    """
    Dummy for ``udev`` structure.
    """
    pass

udev_p = ctypes.POINTER(udev)


class udev_enumerate(ctypes.Structure):
    """
    Dummy for ``udev_enumerate`` structure.
    """


def load_udev_library():
    """
    Load the ``udev`` library and return a :class:`ctypes.CDLL` object for
    it.

    Important functions are given proper signatures and return types to
    support type checking and argument conversion.
    """
    libudev = ctypes.CDLL(find_library('udev'))
    # context function signature
    libudev.udev_new.restype = udev_p
    libudev.udev_unref.argtypes = [udev_p]
    libudev.udev_unref.restype = None
    libudev.udev_ref.argtypes =  [udev_p]
    libudev.udev_ref.restype = udev_p
    libudev.udev_get_sys_path.argtypes = [udev_p]
    libudev.udev_get_sys_path.restype = ctypes.c_char_p
    libudev.udev_get_dev_path.argtypes = [udev_p]
    libudev.udev_get_dev_path.restype = ctypes.c_char_p
    return libudev

