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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import stat

from hypothesis import assume
from hypothesis import given
from hypothesis import strategies
from hypothesis import Settings

import pytest

from pyudev import Devices
from pyudev import DeviceNotFoundAtPathError
from pyudev import DeviceNotFoundByFileError
from pyudev import DeviceNotFoundByNameError
from pyudev import DeviceNotFoundByNumberError
from pyudev import DeviceNotFoundInEnvironmentError

from ._constants import _CONTEXT_STRATEGY
from ._constants import _DEVICE_DATA
from ._constants import _DEVICES
from ._constants import _UDEV_TEST

from ..utils import journal

class TestDevices(object):
    """
    Test ``Devices`` methods.
    """
    # pylint: disable=invalid-name

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=5)
    )
    def test_from_path(self, a_context, device_datum):
        device = Devices.from_path(a_context, device_datum.device_path)
        assert device is not None
        assert device == \
           Devices.from_sys_path(a_context, device_datum.sys_path)
        assert device == Devices.from_path(a_context, device_datum.sys_path)

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=5)
    )
    def test_from_path_strips_leading_slash(self, a_context, device_datum):
        path = device_datum.device_path
        assert Devices.from_path(a_context, path[1:]) == \
               Devices.from_path(a_context, path)

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=5)
    )
    def test_from_sys_path(self, a_context, device_datum):
        device = Devices.from_sys_path(a_context, device_datum.sys_path)
        assert device is not None
        assert device.sys_path == device_datum.sys_path

    @given(_CONTEXT_STRATEGY)
    def test_from_sys_path_device_not_found(self, a_context):
        sys_path = 'there_will_not_be_such_a_device'
        with pytest.raises(DeviceNotFoundAtPathError) as exc_info:
            Devices.from_sys_path(a_context, sys_path)
        error = exc_info.value
        assert error.sys_path == sys_path
        assert str(error) == 'No device at {0!r}'.format(sys_path)

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICES).filter(
          lambda x: len(x.sys_name.split('/')) == 1
       ),
       settings=Settings(max_examples=20)
    )
    def test_from_name(self, a_context, a_device):
        """
        Test that getting a new device based on the name and subsystem
        yields an equivalent device.
        """
        new_device = Devices.from_name(
           a_context,
           a_device.subsystem,
           a_device.sys_name
        )
        assert new_device == a_device

    _devices = [d for d in _DEVICES if len(d.sys_name.split('/')) > 1]
    if len(_devices) > 0:
        @given(
           _CONTEXT_STRATEGY,
           strategies.sampled_from(_devices),
           settings=Settings(max_examples=5)
        )
        def test_from_name_is_path(self, a_context, a_device):
            """
            Lookup using a sys_name which is actually a path should always fail.

            See: rhbz#1263351.
            """
            with pytest.raises(DeviceNotFoundByNameError):
                Devices.from_name(a_context, a_device.subsystem, a_device.sys_name)
    else:
        def test_from_name_is_path(self):
            # pylint: disable=missing-docstring
            pytest.skip("not enough devices with pathlike sysnames")

    @given(_CONTEXT_STRATEGY)
    def test_from_name_no_device_in_existing_subsystem(self, a_context):
        with pytest.raises(DeviceNotFoundByNameError) as exc_info:
            Devices.from_name(a_context, 'block', 'foobar')
        error = exc_info.value
        assert error.subsystem == 'block'
        assert error.sys_name == 'foobar'
        assert str(error) == 'No device {0!r} in {1!r}'.format(
            error.sys_name, error.subsystem)

    @given(_CONTEXT_STRATEGY)
    def test_from_name_nonexisting_subsystem(self, a_context):
        with pytest.raises(DeviceNotFoundByNameError) as exc_info:
            Devices.from_name(a_context, 'no_such_subsystem', 'foobar')
        error = exc_info.value
        assert error.subsystem == 'no_such_subsystem'
        assert error.sys_name == 'foobar'
        assert str(error) == 'No device {0!r} in {1!r}'.format(
            error.sys_name, error.subsystem)

    _device_data = [d for d in _DEVICE_DATA if d.device_node]
    if len(_device_data) > 0:
        @given(
           _CONTEXT_STRATEGY,
           strategies.sampled_from(_device_data),
           settings=Settings(max_examples=5)
        )
        def test_from_device_number(self, a_context, device_datum):
            mode = os.stat(device_datum.device_node).st_mode
            typ = 'block' if stat.S_ISBLK(mode) else 'char'
            device = Devices.from_device_number(
                a_context, typ, device_datum.device_number)
            assert device.device_number == device_datum.device_number
            # make sure, we are really referring to the same device
            assert device.device_path == device_datum.device_path
    else:
        def test_from_device_number(self):
            # pylint: disable=missing-docstring
            pytest.skip("not enough devices with device nodes in data")

    _device_data = [d for d in _DEVICE_DATA if d.device_node]
    if len(_device_data) > 0:
        @given(
           _CONTEXT_STRATEGY,
           strategies.sampled_from(_device_data),
           settings=Settings(max_examples=5)
        )
        def test_from_device_number_wrong_type(
            self,
            a_context,
            device_datum
        ):
            mode = os.stat(device_datum.device_node).st_mode
            # deliberately use the wrong type here to cause either failure
            # or at least device mismatch
            typ = 'char' if stat.S_ISBLK(mode) else 'block'
            try:
                # this either fails, in which case the caught exception is
                # raised, or succeeds, but returns a wrong device
                # (device numbers are not unique across device types)
                device = Devices.from_device_number(
                    a_context, typ, device_datum.device_number)
                # if it succeeds, the resulting device must not match the
                # one, we are actually looking for!
                assert device.device_path != device_datum.device_path
            except DeviceNotFoundByNumberError as error:
                # check the correctness of the exception attributes
                assert error.device_type == typ
                assert error.device_number == device_datum.device_number
    else:
        def test_from_device_number_wrong_type(self):
            # pylint: disable=missing-docstring
            pytest.skip("not enough devices with device nodes in data")

    @given(_CONTEXT_STRATEGY)
    def test_from_device_number_invalid_type(self, a_context):
        with pytest.raises(DeviceNotFoundByNumberError):
            Devices.from_device_number(a_context, 'foobar', 100)

    _device_data = [d for d in _DEVICE_DATA if d.device_node]
    if len(_device_data) > 0:
        @given(
           _CONTEXT_STRATEGY,
           strategies.sampled_from(_device_data),
           settings=Settings(max_examples=5)
        )
        def test_from_device_file(self, a_context, device_datum):
            device = Devices.from_device_file(
               a_context,
               device_datum.device_node
            )
            assert device.device_node == device_datum.device_node
            assert device.device_path == device_datum.device_path
    else:
        def test_from_device_file(self):
            # pylint: disable=missing-docstring
            pytest.skip("not enough devices with device nodes in data")

    _device_data = [d for d in _DEVICE_DATA if d.device_links]
    if len(_device_data) > 0:
        @given(
           _CONTEXT_STRATEGY,
           strategies.sampled_from(_device_data),
           settings=Settings(max_examples=5)
        )
        def test_from_device_file_links(self, a_context, device_datum):
            """
            For each link in DEVLINKS, test that the constructed device's
            path matches the orginal devices path.

            This does not hold true in the case of multipath. In this case
            udevadm's DEVLINKS fields holds some links that do not actually
            point to the originating device.

            See: https://bugzilla.redhat.com/show_bug.cgi?id=1263441.
            """
            device = Devices.from_path(a_context, device_datum.device_path)
            assume(not 'DM_MULTIPATH_DEVICE_PATH' in device)

            for link in device_datum.device_links:
                link = os.path.join(a_context.device_path, link)

                device = Devices.from_device_file(a_context, link)
                assert device.device_path == device_datum.device_path
                assert link in device.device_links
    else:
        def test_from_device_file_links(self):
            # pylint: disable=missing-docstring
            pytest.skip("not enough devices with links in data")

    @given(a_context=_CONTEXT_STRATEGY)
    def test_from_device_file_no_device_file(self, tmpdir, a_context):
        filename = tmpdir.join('test')
        filename.ensure(file=True)
        with pytest.raises(DeviceNotFoundByFileError) as excinfo:
            Devices.from_device_file(a_context, str(filename))
        message = 'not a device file: {0!r}'.format(str(filename))
        assert str(excinfo.value) == message

    @given(a_context=_CONTEXT_STRATEGY)
    def test_from_device_file_non_existing(self, tmpdir, a_context):
        """
        Test that an OSError is raised when constructing a ``Device`` from
        a file that does not actually exist.
        """
        filename = tmpdir.join('test_from_device_file_non_existing')
        assert not tmpdir.check(file=True)
        with pytest.raises(DeviceNotFoundByFileError):
            Devices.from_device_file(a_context, str(filename))

    @_UDEV_TEST(152, "test_from_environment")
    @given(_CONTEXT_STRATEGY)
    def test_from_environment(self, a_context):
        # there is no device in a standard environment
        with pytest.raises(DeviceNotFoundInEnvironmentError):
            Devices.from_environment(a_context)

    _entries = [
       e for e in journal.journal_entries() if e.get('_KERNEL_DEVICE')
    ]
    if len(_entries) > 0:
        @given(
           _CONTEXT_STRATEGY,
           strategies.sampled_from(_entries),
           settings=Settings(max_examples=5)
        )
        def test_from_kernel_device(self, a_context, entry):
            """
            Test that kernel devices can be obtained.
            """
            kernel_device = entry['_KERNEL_DEVICE']
            device = Devices.from_kernel_device(a_context, kernel_device)
            assert device is not None
    else:
        def test_from_kernel_device(self):
            # pylint: disable=missing-docstring
            pytest.skip("not enough journal entries with _KERNEL_DEVICE")

    _entries = [
       e for e in journal.journal_entries() if \
          e.get('_KERNEL_DEVICE') and e.get('_UDEV_SYSNAME')
    ]
    if len(_entries) > 0:
        @given(
           _CONTEXT_STRATEGY,
           strategies.sampled_from(_entries),
           settings=Settings(max_examples=5)
        )
        def test_from_journal_name(self, a_context, entry):
            """
            Test that kernel subsystem combined with udev sysname yields
            a device.
            """
            udev_sysname = entry['_UDEV_SYSNAME']
            subsystem = entry['_KERNEL_SUBSYSTEM']
            device = Devices.from_name(a_context, subsystem, udev_sysname)
            assert device is not None
    else:
        def test_from_journal_name(self):
            # pylint: disable=missing-docstring
            pytest.skip(
               "not enough entries with _KERNEL_SUBSYSTEM and _UDEV_SYSNAME"
            )
