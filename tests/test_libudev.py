# -*- coding: utf-8 -*-
# Copyright (C) 2011, 2012 Sebastian Wiesner <lunaryorn@gmail.com>

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


from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import re
import ctypes

import pytest

from pyudev import _libudev as binding

libudev = binding.libudev


WRAPPER_BLACKLIST_PATTERNS = [
     # vararg functions not supported by ctypes
    'udev_set_log_fn',
    # superfluous in Python, because arbitrary attributes can be attached to
    # objects anyways
    'udev_set_userdata', 'udev_get_userdata',
    # superfluous, because context is already available in .context
    'udev_enumerate_get_udev', 'udev_monitor_get_udev', 'udev_device_get_udev',
    # superfluous, because Python provides already tools to filter lists
    'udev_list_entry_get_by_name',
    # superfluous because of ".encode('string-escape')"
    'udev_util_encode_string',
    # deprecated and removed in recent udev versions
    'udev_monitor_new_from_socket',
    # all queue functions (queue interface is not wrapped)
    re.compile('^udev_queue_.*'),

    # XXX: I've no clue what these functions actually do
    'udev_enumerate_add_syspath',
    'udev_enumerate_scan_subsystems',
]


def _is_blacklisted(function):
    for pattern in WRAPPER_BLACKLIST_PATTERNS:
        if pytest.is_unicode_string(pattern):
            if function.name == pattern:
                return True
        else:
            if pattern.match(function.name):
                return True
    else:
        return False


FUNDAMENTAL_TYPES = {
    'int': ctypes.c_int,
    'char': ctypes.c_char,
    'long long unsigned int': ctypes.c_ulonglong,
    'long unsigned int': ctypes.c_ulong,
    'void': None,
}


def _pointer_to_ctypes(pointer):
    underlying_type = _to_ctypes(pointer.type)
    if underlying_type is ctypes.c_char:
        return ctypes.c_char_p
    else:
        return ctypes.POINTER(underlying_type)


TYPE_CONVERTER = {
    'FundamentalType': lambda t: FUNDAMENTAL_TYPES[t.name],
    'Struct': lambda s: getattr(binding, s.name),
    'PointerType': _pointer_to_ctypes,
    # const qualifiers are ignored in ctypes
    'CvQualifiedType': lambda t: _to_ctypes(t.type),
    # propagate type defs
    'Typedef': lambda t: _to_ctypes(t.type),
}


def _to_ctypes(libudev_type):
    return TYPE_CONVERTER[libudev_type.__class__.__name__](libudev_type)


class LibudevFunction(object):

    def __init__(self, declaration):
        self.declaration = declaration

    @property
    def name(self):
        return self.declaration.name

    @property
    def wrapper(self):
        return getattr(libudev, self.name)

    @property
    def argument_types(self):
        return [_to_ctypes(a) for a in self.declaration.arguments]

    @property
    def return_type(self):
        return _to_ctypes(self.declaration.return_type)


def pytest_funcarg__libudev_function(request):
    """
    Override ``libudev_function`` to skip tests for blacklisted functions.
    """
    function = request.getfuncargvalue('libudev_function')
    if _is_blacklisted(function):
        pytest.skip('{0} is not wrapped'.format(function.name))
    return LibudevFunction(function)


def test_arguments(libudev_function):
    assert libudev_function.wrapper.argtypes == libudev_function.argument_types


def test_return_type(libudev_function):
    # Ignore the return type of *_unref() functions. The return value of these
    # functions is unused in pyudev, so it doesn't need to be wrapped.
    restype = (libudev_function.return_type
               if not libudev_function.name.endswith('_unref')
               else None)
    assert libudev_function.wrapper.restype == restype


def test_error_checker(libudev_function):
    name = libudev_function.name
    if name in binding.ERROR_CHECKERS:
        assert libudev_function.wrapper.errcheck == \
                binding.ERROR_CHECKERS[name]
    else:
        pytest.skip('{0} has no error checker'.format(name))
