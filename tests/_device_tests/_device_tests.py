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


from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import re
import os
import operator
import stat
import gc
import errno
from datetime import timedelta

from hypothesis import given
from hypothesis import strategies
from hypothesis import Settings

import pytest
import mock

from pyudev import Device
from pyudev import DeviceNotFoundAtPathError
from pyudev import DeviceNotFoundByNameError
from pyudev import DeviceNotFoundByNumberError
from pyudev import DeviceNotFoundInEnvironmentError

from pyudev.device import Attributes, Tags

from ._constants import _CONTEXT_STRATEGY
from ._constants import _DEVICE_DATA
from ._constants import _DEVICES
from ._constants import _MIN_SATISFYING_EXAMPLES
from ._constants import _UDEV_TEST

class TestDevice(object):

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=5)
    )
    def test_from_path(self, a_context, device_datum):
        device = Device.from_path(a_context, device_datum.device_path)
        assert device is not None
        assert device == \
           Device.from_sys_path(a_context, device_datum.sys_path)
        assert device == Device.from_path(a_context, device_datum.sys_path)

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=5)
    )
    def test_from_path_strips_leading_slash(self, a_context, device_datum):
        path = device_datum.device_path
        assert Device.from_path(a_context, path[1:]) == \
               Device.from_path(a_context, path)

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=5)
    )
    def test_from_sys_path(self, a_context, device_datum):
        device = Device.from_sys_path(a_context, device_datum.sys_path)
        assert device is not None
        assert device.sys_path == device_datum.sys_path

    @given(_CONTEXT_STRATEGY)
    def test_from_sys_path_device_not_found(self, a_context):
        sys_path = 'there_will_not_be_such_a_device'
        with pytest.raises(DeviceNotFoundAtPathError) as exc_info:
            Device.from_sys_path(a_context, sys_path)
        error = exc_info.value
        assert error.sys_path == sys_path
        assert str(error) == 'No device at {0!r}'.format(sys_path)

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=20)
    )
    def test_from_name(self, a_context, a_device):
        """
        Test that getting a new device based on the name and subsystem
        yields an equivalent device.
        """
        try:
            new_device = Device.from_name(
               a_context,
               a_device.subsystem,
               a_device.sys_name
            )
        except DeviceNotFoundByNameError:
            if len(a_device.sys_name.split("/")) > 1:
                pytest.xfail("rhbz#1263351")
            else:
                raise
        assert new_device == a_device

    @given(_CONTEXT_STRATEGY)
    def test_from_name_no_device_in_existing_subsystem(self, a_context):
        with pytest.raises(DeviceNotFoundByNameError) as exc_info:
            Device.from_name(a_context, 'block', 'foobar')
        error = exc_info.value
        assert error.subsystem == 'block'
        assert error.sys_name == 'foobar'
        assert str(error) == 'No device {0!r} in {1!r}'.format(
            error.sys_name, error.subsystem)

    @given(_CONTEXT_STRATEGY)
    def test_from_name_nonexisting_subsystem(self, a_context):
        with pytest.raises(DeviceNotFoundByNameError) as exc_info:
            Device.from_name(a_context, 'no_such_subsystem', 'foobar')
        error = exc_info.value
        assert error.subsystem == 'no_such_subsystem'
        assert error.sys_name == 'foobar'
        assert str(error) == 'No device {0!r} in {1!r}'.format(
            error.sys_name, error.subsystem)

    _device_data = [d for d in _DEVICE_DATA if d.device_node]
    if len(_device_data) >= _MIN_SATISFYING_EXAMPLES:
        @given(
           _CONTEXT_STRATEGY,
           strategies.sampled_from(_device_data),
           settings=Settings(max_examples=5)
        )
        def test_from_device_number(self, a_context, device_datum):
            mode = os.stat(device_datum.device_node).st_mode
            typ = 'block' if stat.S_ISBLK(mode) else 'char'
            device = Device.from_device_number(
                a_context, typ, device_datum.device_number)
            assert device.device_number == device_datum.device_number
            # make sure, we are really referring to the same device
            assert device.device_path == device_datum.device_path
    else:
        def test_from_device_number(self):
            pytest.skip("not enough devices with device nodes in data")

    _device_data = [d for d in _DEVICE_DATA if d.device_node]
    if len(_device_data) >= _MIN_SATISFYING_EXAMPLES:
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
                device = Device.from_device_number(
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
            pytest.skip("not enough devices with device nodes in data")

    @given(_CONTEXT_STRATEGY)
    def test_from_device_number_invalid_type(self, a_context):
        with pytest.raises(ValueError) as exc_info:
            Device.from_device_number(a_context, 'foobar', 100)
        assert str(exc_info.value).startswith('Invalid type:')

    _device_data = [d for d in _DEVICE_DATA if d.device_node]
    if len(_device_data) >= _MIN_SATISFYING_EXAMPLES:
        @given(
           _CONTEXT_STRATEGY,
           strategies.sampled_from(_device_data),
           settings=Settings(max_examples=5)
        )
        def test_from_device_file(self, a_context, device_datum):
            device = Device.from_device_file(
               a_context,
               device_datum.device_node
            )
            assert device.device_node == device_datum.device_node
            assert device.device_path == device_datum.device_path
    else:
        def test_from_device_file(self):
            pytest.skip("not enough devices with device nodes in data")

    _device_data = [d for d in _DEVICE_DATA if d.device_links]
    if len(_device_data) >= _MIN_SATISFYING_EXAMPLES:
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
            for link in device_datum.device_links:
                link = os.path.join(a_context.device_path, link)
                (linkdir, _) = os.path.split(link)
                devnode = os.path.normpath(
                   os.path.join(linkdir, os.readlink(link))
                )

                try:
                    device = Device.from_device_file(a_context, link)
                    assert device.device_path == device_datum.device_path
                    assert link in device.device_links
                except AssertionError:
                    if devnode != device_datum.device_node:
                        fmt_str = "link %s links to %s, not %s"
                        fmt_args = (link, devnode, device_datum.device_node)
                        pytest.xfail(fmt_str % fmt_args)
                    else:
                        raise
    else:
        def test_from_device_file_links(self):
            pytest.skip("not enough devices with links in data")

    @given(a_context=_CONTEXT_STRATEGY)
    def test_from_device_file_no_device_file(self, tmpdir, a_context):
        filename = tmpdir.join('test')
        filename.ensure(file=True)
        with pytest.raises(ValueError) as excinfo:
            Device.from_device_file(a_context, str(filename))
        message = 'not a device file: {0!r}'.format(str(filename))
        assert str(excinfo.value) == message

    @given(a_context=_CONTEXT_STRATEGY)
    def test_from_device_file_non_existing(self, tmpdir, a_context):
        filename = tmpdir.join('test')
        assert not tmpdir.check(file=True)
        with pytest.raises(EnvironmentError) as excinfo:
            Device.from_device_file(a_context, str(filename))
        pytest.assert_env_error(excinfo.value, errno.ENOENT, str(filename))

    @_UDEV_TEST(152, "test_from_environment")
    @given(_CONTEXT_STRATEGY)
    def test_from_environment(self, a_context):
        # there is no device in a standard environment
        with pytest.raises(DeviceNotFoundInEnvironmentError):
            Device.from_environment(a_context)

    @given(
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=5)
    )
    def test_parent(self, a_device):
        assert a_device.parent is None or \
           isinstance(a_device.parent, Device)

    _devices = [d for d in _DEVICES if d.parent]
    if len(_devices) >= _MIN_SATISFYING_EXAMPLES:
        @_UDEV_TEST(172, "test_child_of_parents")
        @given(
           strategies.sampled_from(_devices),
           settings=Settings(max_examples=5)
        )
        def test_child_of_parent(self, a_device):
            assert a_device in a_device.parent.children
    else:
        @_UDEV_TEST(172, "test_child_of_parents")
        def test_child_of_parent(self):
            pytest.skip("not enough devices with children")

    _devices = [d for d in _DEVICES if d.children]
    if len(_devices) >= _MIN_SATISFYING_EXAMPLES:
        @_UDEV_TEST(172, "test_children")
        @given(
           strategies.sampled_from(_devices),
           settings=Settings(max_examples=5)
        )
        def test_children(self, a_device):
            children = list(a_device.children)
            for child in children:
                assert child != a_device
                assert a_device in child.ancestors
    else:
        @_UDEV_TEST(172, "test_children")
        def test_children(self):
            pytest.skip("not enough devices with children")

    @given(
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=5)
    )
    def test_ancestors(self, a_device):
        child = a_device
        for ancestor in a_device.ancestors:
            assert ancestor == child.parent
            child = ancestor

    _devices = [d for d in _DEVICES if d.find_parent(d.subsystem)]
    if len(_devices) >= _MIN_SATISFYING_EXAMPLES:
        @given(
           strategies.sampled_from(_devices),
           settings=Settings(max_examples=5)
        )
        def test_find_parent(self, a_device):
            parent = a_device.find_parent(a_device.subsystem)
            assert parent.subsystem == a_device.subsystem
            assert parent in a_device.ancestors
    else:
        def test_find_parent(self):
            pytest.skip("not enough devices w/ parents in same subsystem")


    @given(
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=5)
    )
    def test_find_parent_no_devtype_mock(self, a_device):
        funcname = 'udev_device_get_parent_with_subsystem_devtype'
        spec = lambda d, s, t: None
        with mock.patch.object(a_device._libudev, funcname,
                               autospec=spec) as get_parent:
            get_parent.return_value = mock.sentinel.parent_device
            funcname = 'udev_device_ref'
            spec = lambda d: None
            with mock.patch.object(a_device._libudev, funcname,
                                   autospec=spec) as device_ref:
                device_ref.return_value = mock.sentinel.referenced_device
                parent = a_device.find_parent('subsystem')
                assert isinstance(parent, Device)
                assert parent._as_parameter_ is mock.sentinel.referenced_device
                get_parent.assert_called_once_with(
                   a_device,
                   b'subsystem',
                   None
                )
                device_ref.assert_called_once_with(
                   mock.sentinel.parent_device
                )

    @given(
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=5)
    )
    def test_find_parent_with_devtype_mock(self, a_device):
        funcname = 'udev_device_get_parent_with_subsystem_devtype'
        spec = lambda d, s, t: None
        with mock.patch.object(a_device._libudev, funcname,
                               autospec=spec) as get_parent:
            get_parent.return_value = mock.sentinel.parent_device
            funcname = 'udev_device_ref'
            spec = lambda d: None
            with mock.patch.object(a_device._libudev, funcname,
                                   autospec=spec) as device_ref:
                device_ref.return_value = mock.sentinel.referenced_device
                parent = a_device.find_parent('subsystem', 'devtype')
                assert isinstance(parent, Device)
                assert parent._as_parameter_ is mock.sentinel.referenced_device
                get_parent.assert_called_once_with(
                    a_device, b'subsystem', b'devtype')
                device_ref.assert_called_once_with(
                   mock.sentinel.parent_device
                )

    @given(
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=5)
    )
    def test_traverse(self, a_device):
        child = a_device
        for parent in pytest.deprecated_call(a_device.traverse):
            assert parent == child.parent
            child = parent

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=5)
    )
    def test_sys_path(self, a_context, device_datum):
        device = Device.from_path(a_context, device_datum.device_path)
        assert device.sys_path == device_datum.sys_path
        assert pytest.is_unicode_string(device.sys_path)

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=5)
    )
    def test_device_path(self, a_context, device_datum):
        device = Device.from_path(a_context, device_datum.device_path)
        assert device.device_path == device_datum.device_path
        assert pytest.is_unicode_string(device.device_path)

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=5)
    )
    def test_subsystem(self, a_context, device_datum):
        device = Device.from_path(a_context, device_datum.device_path)
        assert device.subsystem == device_datum.properties['SUBSYSTEM']
        assert pytest.is_unicode_string(device.subsystem)

    @given(
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=5)
    )
    def test_device_sys_name(self, a_device):
        assert a_device.sys_name.replace('/', '!') == \
           os.path.basename(a_device.device_path)
        assert pytest.is_unicode_string(a_device.sys_name)

    @given(
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=5)
    )
    def test_sys_number(self, a_device):
        match = re.search(r'\d+$', a_device.sys_name)
        # filter out devices with completely nummeric names (first character
        # doesn't count according to the implementation of libudev)
        if match and match.start() > 1:
            assert a_device.sys_number == match.group(0)
            assert pytest.is_unicode_string(a_device.sys_name)
        else:
            assert a_device.sys_number is None

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=5)
    )
    def test_type(self, a_context, device_datum):
        device = Device.from_path(a_context, device_datum.device_path)
        assert device.device_type == device_datum.properties.get('DEVTYPE')
        if device.device_type:
            assert pytest.is_unicode_string(device.device_type)

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=5)
    )
    def test_driver(self, a_context, device_datum):
        device = Device.from_path(a_context, device_datum.device_path)
        assert device.driver == device_datum.properties.get('DRIVER')
        if device.driver:
            assert pytest.is_unicode_string(device.driver)

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=5)
    )
    def test_device_node(self, a_context, device_datum):
        device = Device.from_path(a_context, device_datum.device_path)
        assert device.device_node == device_datum.device_node
        if device.device_node:
            assert pytest.is_unicode_string(device.device_node)

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=5)
    )
    def test_device_number(self, a_context, device_datum):
        device = Device.from_path(a_context, device_datum.device_path)
        assert device.device_number == device_datum.device_number

    @_UDEV_TEST(165, "test_is_initialized")
    @given(
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=5)
    )
    def test_is_initialized(self, a_device):
        assert isinstance(a_device.is_initialized, bool)

    @_UDEV_TEST(165, "test_is_initialized_mock")
    @given(
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=5)
    )
    def test_is_initialized_mock(self, a_device):
        funcname = 'udev_device_get_is_initialized'
        spec = lambda d: None
        with mock.patch.object(a_device._libudev, funcname,
                               autospec=spec) as func:
            func.return_value = False
            assert not a_device.is_initialized
            func.assert_called_once_with(a_device)

    @_UDEV_TEST(165, "test_time_since_initialized")
    @given(
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=5)
    )
    def test_time_since_initialized(self, a_device):
        assert isinstance(a_device.time_since_initialized, timedelta)

    @_UDEV_TEST(165, "test_time_since_initialized_mock")
    @given(
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=5)
    )
    def test_time_since_initialized_mock(self, a_device):
        funcname = 'udev_device_get_usec_since_initialized'
        spec = lambda d: None
        with mock.patch.object(a_device._libudev, funcname,
                               autospec=spec) as func:
            func.return_value = 100
            assert a_device.time_since_initialized.microseconds == 100
            func.assert_called_once_with(a_device)

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=5)
    )
    def test_links(self, a_context, device_datum):
        device = Device.from_path(a_context, device_datum.device_path)
        assert sorted(device.device_links) == sorted(device_datum.device_links)
        for link in device.device_links:
            assert pytest.is_unicode_string(link)

    @given(
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=5)
    )
    def test_action(self, a_device):
        assert a_device.action is None

    @given(
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=5)
    )
    def test_action_mock(self, a_device):
        funcname = 'udev_device_get_action'
        spec = lambda d: None
        with mock.patch.object(a_device._libudev, funcname,
                               autospec=spec) as func:
            func.return_value = b'spam'
            assert a_device.action == 'spam'
            func.assert_called_once_with(a_device)
            func.reset_mock()
            assert pytest.is_unicode_string(a_device.action)
            func.assert_called_once_with(a_device)

    @given(
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=5)
    )
    def test_sequence_number(self, a_device):
        assert a_device.sequence_number == 0

    @given(
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=5)
    )
    def test_attributes(self, a_device):
        # see TestAttributes for complete attribute tests
        assert isinstance(a_device.attributes, Attributes)

    @given(_CONTEXT_STRATEGY)
    def test_no_leak(self, a_context):
        """
        Regression test for issue #32, modelled after the script which revealed
        this issue.

        The leak was caused by the following reference cycle between
        ``Attributes`` and ``Device``:

        Device._attributes -> Attributes.device

        https://github.com/lunaryorn/pyudev/issues/32
        """
        for _ in a_context.list_devices(subsystem='usb'):
            pass
        # make sure that no memory leaks
        assert not gc.garbage

    @given(
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=5)
    )
    def test_tags(self, a_device):
        # see TestTags for complete tag tests
        assert isinstance(a_device.tags, Tags)

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=5)
    )
    def test_iteration(self, a_context, device_datum):
        device = Device.from_path(a_context, device_datum.device_path)
        for property in device:
            assert pytest.is_unicode_string(property)
        # test that iteration really yields all properties
        device_properties = set(device)
        for property in device_datum.properties:
            assert property in device_properties

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=5)
    )
    def test_length(self, a_context, device_datum):
        device = Device.from_path(a_context, device_datum.device_path)
        assert len(device) == len(device_datum.properties)

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=5)
    )
    def test_getitem(self, a_context, device_datum):
        device = Device.from_path(a_context, device_datum.device_path)
        for prop in device_datum.properties:
            assert device[prop] == device_datum.properties[prop]

    _device_data = [d for d in _DEVICE_DATA if 'DEVNAME' in d.properties]
    if len(_device_data) >= _MIN_SATISFYING_EXAMPLES:
        @given(
           _CONTEXT_STRATEGY,
           strategies.sampled_from(_device_data),
           settings=Settings(max_examples=5)
        )
        def test_getitem_devname(self, a_context, device_datum):
            device = Device.from_path(a_context, device_datum.device_path)
            data_devname = os.path.join(
                a_context.device_path, device_datum.properties['DEVNAME'])
            device_devname = os.path.join(a_context.device_path, device['DEVNAME'])
            assert device_devname == data_devname
    else:
        def test_getitem_devname(self):
            pytest.skip("not enough devices with 'DEVNAME' in properties")

    @given(
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=5)
    )
    def test_getitem_nonexisting(self, a_device):
        with pytest.raises(KeyError) as excinfo:
            # pylint: disable=pointless-statement
            a_device['a non-existing property']
        assert str(excinfo.value) == repr('a non-existing property')

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=5)
    )
    def test_asint(self, a_context, device_datum):
        device = Device.from_path(a_context, device_datum.device_path)
        for property, value in device_datum.properties.items():
            try:
                value = int(value)
            except ValueError:
                with pytest.raises(ValueError):
                    device.asint(property)
            else:
                assert device.asint(property) == value

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=5)
    )
    def test_asbool(self, a_context, device_datum):
        device = Device.from_path(a_context, device_datum.device_path)
        for prop, value in device_datum.properties.items():
            if value == '1':
                assert device.asbool(prop)
            elif value == '0':
                assert not device.asbool(prop)
            else:
                with pytest.raises(ValueError) as exc_info:
                    device.asbool(prop)
                message = 'Not a boolean value: {0!r}'
                assert str(exc_info.value) == message.format(value)

    @given(
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=5)
    )
    def test_hash(self, a_device):
        assert hash(a_device) == hash(a_device.device_path)
        assert hash(a_device.parent) == hash(a_device.parent)
        assert hash(a_device.parent) != hash(a_device)

    @given(
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=5)
    )
    def test_equality(self, a_device):
        assert a_device == a_device.device_path
        assert a_device == a_device
        assert a_device.parent == a_device.parent
        # pylint: disable=superfluous-parens
        assert not (a_device == a_device.parent)

    @given(
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=5)
    )
    def test_inequality(self, a_device):
        # pylint: disable=superfluous-parens
        assert not (a_device != a_device.device_path)
        assert not (a_device != a_device)
        assert not (a_device.parent != a_device.parent)
        assert a_device != a_device.parent

    @given(
       strategies.sampled_from(
          [operator.ge, operator.gt, operator.le, operator.lt]
       ),
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=4)
    )
    def test_device_ordering(self, an_operator, a_device):
        with pytest.raises(TypeError) as exc_info:
            an_operator(a_device, a_device)
        assert str(exc_info.value) == 'Device not orderable'
