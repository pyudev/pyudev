# -*- coding: utf-8 -*-
# Copyright (C) 2011 Sebastian Wiesner <lunaryorn@googlemail.com>

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

import pytest

from pyudev import _libudev as binding

libudev = binding.libudev


# new functions added in specific libudev versions
UDEV_ADDITIONS = {
    152: ['udev_new_from_environment'],
    154: ['udev_device_get_tags_list_entry',
          'udev_enumerate_add_match_tag',
          'udev_monitor_filter_add_match_tag'],
    165: ['udev_device_get_is_initialized',
          'udev_device_get_usec_since_initialized',
          'udev_enumerate_add_match_is_initialized'],
    167: ['udev_get_run_path',
          'udev_device_get_sysattr_list_entry'],
    172: ['udev_device_has_tag', 'udev_enumerate_add_match_parent'],
    }


def pytest_generate_tests(metafunc):
    if 'funcname' in metafunc.funcargnames:
        for namespace, members in binding.SIGNATURES.items():
            for funcname in members:
                full_name = '{0}_{1}'.format(namespace, funcname)
                metafunc.addcall(param=(namespace, funcname), id=full_name,
                                 funcargs=dict(funcname=full_name))
    if metafunc.function.__name__ == 'test_missing_functions':
        for version, functions in UDEV_ADDITIONS.items():
            for function in functions:
                funcargs = dict(version=version, missing_function=function)
                testid = 'version {0}, {1}'.format(version, function)
                metafunc.addcall(funcargs=funcargs, id=testid)


def pytest_funcarg__signature(request):
    namespace, name = request.param
    return binding.SIGNATURES[namespace][name]


def pytest_funcarg__argtypes(request):
    argtypes, _ = request.getfuncargvalue('signature')
    return argtypes


def pytest_funcarg__restype(request):
    _, restype = request.getfuncargvalue('signature')
    return restype


def pytest_funcarg__errcheck(request):
    funcname = request.getfuncargvalue('funcname')
    return binding.ERROR_CHECKERS.get(funcname)


@pytest.need_udev_version('>= {0}'.format(max(UDEV_ADDITIONS)))
def test_presence(funcname):
    assert hasattr(libudev, funcname)


def test_signatures(funcname, restype, argtypes, errcheck):
    func = getattr(libudev, funcname, None)
    if not func:
        pytest.skip('{0} not available'.format(funcname))
    assert func.restype == restype
    if not argtypes:
        assert not func.argtypes
    else:
        assert func.argtypes == argtypes
    assert func.errcheck == errcheck


def test_missing_functions(version, missing_function):
    if pytest.config.udev_version >= version:
        pytest.skip('{0} already exists in {1}'.format(
            missing_function, pytest.config.udev_version))
    assert not hasattr(libudev, missing_function)
