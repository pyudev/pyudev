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

udev_enumerate_p = ctypes.POINTER(udev_enumerate)


class udev_list_entry(ctypes.Structure):
    """
    Dummy for ``udev_list_entry`` structure.
    """

udev_list_entry_p = ctypes.POINTER(udev_list_entry)


SIGNATURES = {
    # context
    'udev': dict(
        new=(None, udev_p),
        unref=([udev_p], None),
        ref=([udev_p], udev_p),
        get_sys_path=([udev_p], ctypes.c_char_p),
        get_dev_path=([udev_p], ctypes.c_char_p)),
    # enumeration
    'udev_enumerate': dict(
        new=([udev_p], udev_enumerate_p),
        ref=([udev_enumerate_p], udev_enumerate_p),
        unref=([udev_enumerate_p], None),
        add_match_subsystem=([udev_enumerate_p, ctypes.c_char_p], int),
        add_match_property=(
            [udev_enumerate_p, ctypes.c_char_p, ctypes.c_char_p], int),
        scan_devices=([udev_enumerate_p], int),
        get_list_entry=([udev_enumerate_p], udev_list_entry_p)),
    # list entries
    'udev_list_entry': dict(
        get_next=([udev_list_entry_p], udev_list_entry_p),
        get_name=([udev_list_entry_p], ctypes.c_char_p),
        get_value=([udev_list_entry_p], ctypes.c_char_p)),
    }


def load_udev_library():
    """
    Load the ``udev`` library and return a :class:`ctypes.CDLL` object for
    it.

    Important functions are given proper signatures and return types to
    support type checking and argument conversion.
    """
    libudev = ctypes.CDLL(find_library('udev'))
    # context function signature
    for namespace, members in SIGNATURES.iteritems():
        for funcname, signature in members.iteritems():
            funcname = '{0}_{1}'.format(namespace, funcname)
            func = getattr(libudev, funcname)
            argtypes, restype = signature
            func.argtypes = argtypes
            func.restype = restype
    return libudev

