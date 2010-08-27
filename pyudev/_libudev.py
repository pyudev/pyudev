# -*- coding: utf-8 -*-
# Copyright (c) 2010 Sebastian Wiesner <lunaryorn@googlemail.com>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.


"""
    _libudev
    ========

    Wrapper types for libudev.  Use ``libudev`` attribute to access libudev
    functions.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""


from ctypes import CDLL, Structure, POINTER, c_char_p, c_int, get_errno
from ctypes.util import find_library


class udev(Structure):
    """
    Dummy for ``udev`` structure.
    """
    pass

udev_p = POINTER(udev)


class udev_enumerate(Structure):
    """
    Dummy for ``udev_enumerate`` structure.
    """

udev_enumerate_p = POINTER(udev_enumerate)


class udev_list_entry(Structure):
    """
    Dummy for ``udev_list_entry`` structure.
    """

udev_list_entry_p = POINTER(udev_list_entry)


class udev_device(Structure):
    """
    Dummy for ``udev_device`` structure.
    """

udev_device_p = POINTER(udev_device)


class udev_monitor(Structure):
    """
    Dummy for ``udev_device`` structure.
    """

udev_monitor_p = POINTER(udev_monitor)


SIGNATURES = {
    # context
    'udev': dict(
        new=(None, udev_p),
        unref=([udev_p], None),
        ref=([udev_p], udev_p),
        get_sys_path=([udev_p], c_char_p),
        get_dev_path=([udev_p], c_char_p)),
    # enumeration
    'udev_enumerate': dict(
        new=([udev_p], udev_enumerate_p),
        ref=([udev_enumerate_p], udev_enumerate_p),
        unref=([udev_enumerate_p], None),
        add_match_subsystem=([udev_enumerate_p, c_char_p], int),
        add_match_property=([udev_enumerate_p, c_char_p, c_char_p], int),
        scan_devices=([udev_enumerate_p], int),
        get_list_entry=([udev_enumerate_p], udev_list_entry_p)),
    # list entries
    'udev_list_entry': dict(
        get_next=([udev_list_entry_p], udev_list_entry_p),
        get_name=([udev_list_entry_p], c_char_p),
        get_value=([udev_list_entry_p], c_char_p)),
    # devices
    'udev_device': dict(
        ref=([udev_device_p], udev_device_p),
        unref=([udev_device_p], None),
        new_from_syspath=([udev_p, c_char_p], udev_device_p),
        get_parent=([udev_device_p], udev_device_p),
        get_devpath=([udev_device_p], c_char_p),
        get_subsystem=([udev_device_p], c_char_p),
        get_syspath=([udev_device_p], c_char_p),
        get_sysname=([udev_device_p], c_char_p),
        get_devnode=([udev_device_p], c_char_p),
        get_property_value=([udev_device_p, c_char_p], c_char_p),
        get_sysattr_value=([udev_device_p, c_char_p], c_char_p),
        get_action=([udev_device_p], c_char_p),
        get_devlinks_list_entry=([udev_device_p], udev_list_entry_p),
        get_properties_list_entry=([udev_device_p], udev_list_entry_p)),
    # monitoring
    'udev_monitor': dict(
        ref=([udev_monitor_p], udev_monitor_p),
        unref=([udev_monitor_p], None),
        new_from_netlink=([udev_p, c_char_p], udev_monitor_p),
        new_from_socket=([udev_p, c_char_p], udev_monitor_p),
        enable_receiving=([udev_monitor_p], c_int),
        get_fd=([udev_monitor_p], c_int),
        receive_device=([udev_monitor_p], udev_device_p),
        filter_add_match_subsystem_devtype=(
            [udev_monitor_p, c_char_p, c_char_p], c_int))
    }


def load_udev_library():
    """
    Load the ``udev`` library and return a :class:`ctypes.CDLL` object for
    it.  The library has errno handling enabled.

    Important functions are given proper signatures and return types to
    support type checking and argument conversion.
    """
    libudev = CDLL(find_library('udev'), use_errno=True)
    # context function signature
    for namespace, members in SIGNATURES.iteritems():
        for funcname, signature in members.iteritems():
            funcname = '{0}_{1}'.format(namespace, funcname)
            func = getattr(libudev, funcname)
            argtypes, restype = signature
            func.argtypes = argtypes
            func.restype = restype
    return libudev


libudev = load_udev_library()


def get_libudev_errno():
    return get_errno()


