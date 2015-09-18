# -*- coding: utf-8 -*-
# Copyright (C) 2010, 2011, 2012, 2013 Sebastian Wiesner <lunaryorn@gmail.com>

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
    _libudev
    ========

    Wrapper types for libudev.  Use ``libudev`` attribute to access libudev
    functions.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@gmail.com>
"""


from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from ctypes import (CDLL, Structure, POINTER,
                    c_char, c_char_p, c_int, c_uint, c_ulonglong)
from ctypes.util import find_library

from pyudev._errorcheckers import (check_negative_errorcode,
                                   check_errno_on_nonzero_return,
                                   check_errno_on_null_pointer_return)


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

class udev_hwdb(Structure):
    """
    Dummy for ``udev_hwdb`` structure.
    """

udev_hwdb_p = POINTER(udev_hwdb)


dev_t = c_ulonglong


SIGNATURES = {
    # context
    'udev': dict(
        new=([], udev_p),
        unref=([udev_p], None),
        ref=([udev_p], udev_p),
        get_sys_path=([udev_p], c_char_p),
        get_dev_path=([udev_p], c_char_p),
        get_run_path=([udev_p], c_char_p),
        get_log_priority=([udev_p], c_int),
        set_log_priority=([udev_p, c_int], None)),
    # enumeration
    'udev_enumerate': dict(
        new=([udev_p], udev_enumerate_p),
        ref=([udev_enumerate_p], udev_enumerate_p),
        unref=([udev_enumerate_p], None),
        add_match_subsystem=([udev_enumerate_p, c_char_p], c_int),
        add_nomatch_subsystem=([udev_enumerate_p, c_char_p], c_int),
        add_match_property=([udev_enumerate_p, c_char_p, c_char_p], c_int),
        add_match_sysattr=([udev_enumerate_p, c_char_p, c_char_p], c_int),
        add_nomatch_sysattr=([udev_enumerate_p, c_char_p, c_char_p], c_int),
        add_match_tag=([udev_enumerate_p, c_char_p], c_int),
        add_match_sysname=([udev_enumerate_p, c_char_p], c_int),
        add_match_parent=([udev_enumerate_p, udev_device_p], c_int),
        add_match_is_initialized=([udev_enumerate_p], c_int),
        scan_devices=([udev_enumerate_p], c_int),
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
        new_from_subsystem_sysname=([udev_p, c_char_p, c_char_p],
                                    udev_device_p),
        new_from_devnum=([udev_p, c_char, dev_t], udev_device_p),
        new_from_device_id=([udev_p, c_char_p], udev_device_p),
        new_from_environment=([udev_p], udev_device_p),
        get_parent=([udev_device_p], udev_device_p),
        get_parent_with_subsystem_devtype=([udev_device_p, c_char_p, c_char_p],
                                           udev_device_p),
        get_devpath=([udev_device_p], c_char_p),
        get_subsystem=([udev_device_p], c_char_p),
        get_syspath=([udev_device_p], c_char_p),
        get_sysnum=([udev_device_p], c_char_p),
        get_sysname=([udev_device_p], c_char_p),
        get_driver=([udev_device_p], c_char_p),
        get_devtype=([udev_device_p], c_char_p),
        get_devnode=([udev_device_p], c_char_p),
        get_property_value=([udev_device_p, c_char_p], c_char_p),
        get_sysattr_value=([udev_device_p, c_char_p], c_char_p),
        get_devnum=([udev_device_p], dev_t),
        get_action=([udev_device_p], c_char_p),
        get_seqnum=([udev_device_p], c_ulonglong),
        get_is_initialized=([udev_device_p], c_int),
        get_usec_since_initialized=([udev_device_p], c_ulonglong),
        get_devlinks_list_entry=([udev_device_p], udev_list_entry_p),
        get_tags_list_entry=([udev_device_p], udev_list_entry_p),
        get_properties_list_entry=([udev_device_p], udev_list_entry_p),
        get_sysattr_list_entry=([udev_device_p], udev_list_entry_p),
        set_sysattr_value=([udev_device_p, c_char_p, c_char_p], c_int),
        has_tag=([udev_device_p, c_char_p], c_int)),
    # monitoring
    'udev_monitor': dict(
        ref=([udev_monitor_p], udev_monitor_p),
        unref=([udev_monitor_p], None),
        new_from_netlink=([udev_p, c_char_p], udev_monitor_p),
        enable_receiving=([udev_monitor_p], c_int),
        set_receive_buffer_size=([udev_monitor_p, c_int], c_int),
        get_fd=([udev_monitor_p], c_int),
        receive_device=([udev_monitor_p], udev_device_p),
        filter_add_match_subsystem_devtype=(
            [udev_monitor_p, c_char_p, c_char_p], c_int),
        filter_add_match_tag=([udev_monitor_p, c_char_p], c_int),
        filter_update=([udev_monitor_p], c_int),
        filter_remove=([udev_monitor_p], c_int)),
    # hwdb
    'udev_hwdb': dict(
        ref=([udev_hwdb_p], udev_hwdb_p),
        unref=([udev_hwdb_p], None),
        new=([udev_p], udev_hwdb_p),
        get_properties_list_entry=([udev_hwdb_p, c_char_p, c_uint], udev_list_entry_p))
}


ERROR_CHECKERS = dict(
    udev_device_get_action=None,
    udev_device_get_devlinks_list_entry=None,
    udev_device_get_devnode=None,
    udev_device_get_devnum=None,
    udev_device_get_devpath=None,
    udev_device_get_devtype=None,
    udev_device_get_driver=None,
    udev_device_get_is_initialized=None,
    udev_device_get_parent=None,
    udev_device_get_parent_with_subsystem_devtype=None,
    udev_device_get_properties_list_entry=None,
    udev_device_get_property_value=None,
    udev_device_get_seqnum=None,
    udev_device_get_subsystem=None,
    udev_device_get_sysattr_list_entry=None,
    udev_device_get_sysattr_value=None,
    udev_device_get_sysname=None,
    udev_device_get_sysnum=None,
    udev_device_get_syspath=None,
    udev_device_get_tags_list_entry=None,
    udev_device_get_usec_since_initialized=None,
    udev_device_has_tag=None,
    udev_device_new_from_device_id=None,
    udev_device_new_from_devnum=None,
    udev_device_new_from_environment=None,
    udev_device_new_from_subsystem_sysname=None,
    udev_device_new_from_syspath=None,
    udev_device_ref=None,
    udev_device_unref=None,
    udev_device_set_sysattr_value=check_negative_errorcode,
    udev_enumerate_add_match_parent=check_negative_errorcode,
    udev_enumerate_add_match_subsystem=check_negative_errorcode,
    udev_enumerate_add_nomatch_subsystem=check_negative_errorcode,
    udev_enumerate_add_match_property=check_negative_errorcode,
    udev_enumerate_add_match_sysattr=check_negative_errorcode,
    udev_enumerate_add_nomatch_sysattr=check_negative_errorcode,
    udev_enumerate_add_match_tag=check_negative_errorcode,
    udev_enumerate_add_match_sysname=check_negative_errorcode,
    udev_enumerate_add_match_is_initialized=check_negative_errorcode,
    udev_enumerate_get_list_entry=None,
    udev_enumerate_new=None,
    udev_enumerate_ref=None,
    udev_enumerate_scan_devices=None,
    udev_enumerate_unref=None,
    udev_get_dev_path=None,
    udev_get_log_priority=None,
    udev_get_run_path=None,
    udev_get_sys_path=None,
    udev_hwdb_get_properties_list_entry=None,
    udev_hwdb_new=None,
    udev_hwdb_ref=None,
    udev_hwdb_unref=None,
    udev_list_entry_get_name=None,
    udev_list_entry_get_next=None,
    udev_list_entry_get_value=None,
    udev_monitor_set_receive_buffer_size=check_errno_on_nonzero_return,
    # libudev doc says, enable_receiving returns a negative errno, but tests
    # show that this is not reliable, so query the real error code
    udev_monitor_enable_receiving=check_errno_on_nonzero_return,
    udev_monitor_receive_device=check_errno_on_null_pointer_return,
    udev_monitor_ref=None,
    udev_monitor_filter_add_match_subsystem_devtype=check_negative_errorcode,
    udev_monitor_filter_add_match_tag=check_negative_errorcode,
    udev_monitor_filter_update=check_errno_on_nonzero_return,
    udev_monitor_filter_remove=check_errno_on_nonzero_return,
    udev_monitor_get_fd=None,
    udev_monitor_new_from_netlink=None,
    udev_monitor_unref=None,
    udev_new=None,
    udev_ref=None,
    udev_set_log_priority=None,
    udev_unref=None
)


def load_udev_library():
    """
    Load the ``udev`` library and return a :class:`ctypes.CDLL` object for
    it.  The library has errno handling enabled.

    Important functions are given proper signatures and return types to
    support type checking and argument conversion.

    Raise :exc:`~exceptions.ImportError`, if the udev library was not found.
    """
    udev_library_name = find_library('udev')
    if not udev_library_name:
        raise ImportError('No library named udev')
    libudev = CDLL(udev_library_name, use_errno=True)
    # context function signature
    for namespace, members in SIGNATURES.items():
        for funcname in members:
            fullname = '{0}_{1}'.format(namespace, funcname)
            func = getattr(libudev, fullname, None)
            if func:
                argtypes, restype = members[funcname]
                func.argtypes = argtypes
                func.restype = restype
                errorchecker = ERROR_CHECKERS.get(fullname)
                if errorchecker:
                    func.errcheck = errorchecker
    return libudev
