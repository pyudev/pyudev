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
Tests methods belonging to Devices class.

.. moduleauthor::  mulhern <amulhern@redhat.com>
"""

# isort: FUTURE
from __future__ import absolute_import, division, print_function, unicode_literals

# isort: STDLIB
import os
import stat

# isort: THIRDPARTY
import pytest
from hypothesis import assume, given, settings

# isort: LOCAL
from pyudev import (
    DeviceNotFoundAtPathError,
    DeviceNotFoundByFileError,
    DeviceNotFoundByNameError,
    DeviceNotFoundByNumberError,
    DeviceNotFoundInEnvironmentError,
    Devices,
)

from .._constants import (
    _CONTEXT,
    _CONTEXT_STRATEGY,
    _SUBSYSTEM_STRATEGY,
    _UDEV_TEST,
    device_strategy,
)
from ..utils import failed_health_check_wrapper


class TestDevices(object):
    """
    Test ``Devices`` methods.
    """

    # pylint: disable=invalid-name

    @given(_CONTEXT_STRATEGY, device_strategy())
    @settings(max_examples=5)
    def test_from_path(self, a_context, a_device):
        """
        from_path() method yields correct device.
        """
        assert a_device == Devices.from_path(a_context, a_device.device_path)

    @given(_CONTEXT_STRATEGY, device_strategy())
    @settings(max_examples=5)
    def test_from_path_strips_leading_slash(self, a_context, a_device):
        """
        from_path() yields the same value, even if initial '/' is missing.
        """
        path = a_device.device_path
        assert Devices.from_path(a_context, path[1:]) == Devices.from_path(
            a_context, path
        )

    @given(_CONTEXT_STRATEGY, device_strategy())
    @settings(max_examples=5)
    def test_from_sys_path(self, a_context, a_device):
        """
        from_sys_path() yields the correct device.
        """
        assert a_device == Devices.from_sys_path(a_context, a_device.sys_path)

    def test_from_sys_path_device_not_found(self):
        """
        Verify that a non-existant sys_path causes an exception.
        """
        sys_path = "there_will_not_be_such_a_device"
        with pytest.raises(DeviceNotFoundAtPathError) as exc_info:
            Devices.from_sys_path(_CONTEXT, sys_path)
        error = exc_info.value
        assert error.sys_path == sys_path

    @given(_CONTEXT_STRATEGY, device_strategy())
    @settings(max_examples=5)
    def test_from_name(self, a_context, a_device):
        """
        Test that getting a new device based on the name and subsystem
        yields an equivalent device.
        """
        new_device = Devices.from_name(a_context, a_device.subsystem, a_device.sys_name)
        assert new_device == a_device

    @given(_CONTEXT_STRATEGY, _SUBSYSTEM_STRATEGY)
    @settings(max_examples=5)
    def test_from_name_no_device_in_existing_subsystem(self, a_context, subsys):
        """
        Verify that a real subsystem and non-existant name causes an
        exception to be raised.
        """
        with pytest.raises(DeviceNotFoundByNameError) as exc_info:
            Devices.from_name(a_context, subsys, "foobar")
        error = exc_info.value
        assert error.subsystem == subsys
        assert error.sys_name == "foobar"

    def test_from_name_nonexisting_subsystem(self):
        """
        Verify that a non-existant subsystem causes an exception.
        """
        with pytest.raises(DeviceNotFoundByNameError) as exc_info:
            Devices.from_name(_CONTEXT, "no_such_subsystem", "foobar")
        error = exc_info.value
        assert error.subsystem == "no_such_subsystem"
        assert error.sys_name == "foobar"

    @failed_health_check_wrapper
    @given(
        _CONTEXT_STRATEGY,
        device_strategy(filter_func=lambda x: x.device_node is not None),
    )
    @settings(max_examples=5)
    def test_from_device_number(self, a_context, a_device):
        """
        Verify that from_device_number() yields the correct device.
        """
        mode = os.stat(a_device.device_node).st_mode
        typ = "block" if stat.S_ISBLK(mode) else "char"
        device = Devices.from_device_number(a_context, typ, a_device.device_number)
        assert a_device == device

    @failed_health_check_wrapper
    @given(
        _CONTEXT_STRATEGY,
        device_strategy(filter_func=lambda x: x.device_node is not None),
    )
    @settings(max_examples=5)
    def test_from_device_number_wrong_type(self, a_context, a_device):
        """
        Verify appropriate behavior on real device number but swapped
        subsystems.
        """
        mode = os.stat(a_device.device_node).st_mode
        # deliberately use the wrong type here to cause either failure
        # or at least device mismatch
        typ = "char" if stat.S_ISBLK(mode) else "block"
        try:
            # this either fails, in which case the caught exception is
            # raised, or succeeds, but returns a wrong device
            # (device numbers are not unique across device types)
            device = Devices.from_device_number(a_context, typ, a_device.device_number)
            # if it succeeds, the resulting device must not match the
            # one, we are actually looking for!
            assert device != a_device
        except DeviceNotFoundByNumberError as error:
            # check the correctness of the exception attributes
            assert error.device_type == typ
            assert error.device_number == a_device.device_number

    def test_from_device_number_invalid_type(self):
        """
        Verify that a non-existant subsystem always results in an exception.
        """
        with pytest.raises(DeviceNotFoundByNumberError):
            Devices.from_device_number(_CONTEXT, "foobar", 100)

    @failed_health_check_wrapper
    @given(
        _CONTEXT_STRATEGY,
        device_strategy(filter_func=lambda x: x.device_node is not None),
    )
    @settings(max_examples=5)
    def test_from_device_file(self, a_context, a_device):
        """
        Verify that from_device_file() yields correct device.
        """
        device = Devices.from_device_file(a_context, a_device.device_node)
        assert a_device == device

    def test_from_device_file_no_device_file(self, tmpdir):
        """
        Verify that a file that is not a device file will cause an exception
        to be raised.
        """
        filename = tmpdir.join("test")
        filename.ensure(file=True)
        with pytest.raises(DeviceNotFoundByFileError):
            Devices.from_device_file(_CONTEXT, str(filename))

    def test_from_device_file_non_existing(self, tmpdir):
        """
        Test that an OSError is raised when constructing a ``Device`` from
        a file that does not actually exist.
        """
        filename = tmpdir.join("test_from_device_file_non_existing")
        assert not tmpdir.check(file=True)
        with pytest.raises(DeviceNotFoundByFileError):
            Devices.from_device_file(_CONTEXT, str(filename))

    @_UDEV_TEST(152, "test_from_environment")
    def test_from_environment(self):
        """
        there is no device in a standard environment
        """
        with pytest.raises(DeviceNotFoundInEnvironmentError):
            Devices.from_environment(_CONTEXT)
