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
Tests methods belonging to Device class.

.. moduleauthor::  mulhern <amulhern@redhat.com>
"""

# isort: FUTURE
from __future__ import absolute_import, division, print_function, unicode_literals

# isort: STDLIB
import gc
import operator
import os
import re
from datetime import timedelta

# isort: THIRDPARTY
import pytest
from hypothesis import given, settings, strategies

# isort: LOCAL
from pyudev import Device, Devices
from pyudev.device import Attributes, Tags

from .._constants import _CONTEXT, _CONTEXT_STRATEGY, _DEVICE_DATA, _DEVICES, _UDEV_TEST
from ..utils import is_unicode_string

try:
    from unittest import mock
except ImportError:
    import mock


class TestDevice(object):
    """
    Test ``Device`` methods.
    """

    @given(strategies.sampled_from(_DEVICES))
    @settings(max_examples=5)
    def test_parent(self, a_device):
        assert a_device.parent is None or isinstance(a_device.parent, Device)

    _devices = [d for d in _DEVICES if d.parent is not None]

    @pytest.mark.skipif(len(_devices) == 0, reason="no device with a parent")
    @_UDEV_TEST(172, "test_child_of_parents")
    @given(strategies.sampled_from(_devices))
    @settings(max_examples=5)
    def test_child_of_parent(self, a_device):
        assert a_device in a_device.parent.children

    _devices = [d for d in _DEVICES if list(d.children)]

    @pytest.mark.skipif(len(_devices) == 0, reason="no device with a child")
    @_UDEV_TEST(172, "test_children")
    @given(strategies.sampled_from(_devices))
    @settings(max_examples=5)
    def test_children(self, a_device):
        children = list(a_device.children)
        for child in children:
            assert child != a_device
            assert a_device in child.ancestors

    @given(strategies.sampled_from(_DEVICES))
    @settings(max_examples=5)
    def test_ancestors(self, a_device):
        child = a_device
        for ancestor in a_device.ancestors:
            assert ancestor == child.parent
            child = ancestor

    _devices = [d for d in _DEVICES if d.find_parent(d.subsystem) is not None]

    @pytest.mark.skipif(
        len(_devices) == 0, reason="no device with a parent in the same subsystem"
    )
    @given(strategies.sampled_from(_devices))
    @settings(max_examples=5)
    def test_find_parent(self, a_device):
        parent = a_device.find_parent(a_device.subsystem)
        assert parent.subsystem == a_device.subsystem
        assert parent in a_device.ancestors

    @given(strategies.sampled_from(_DEVICES))
    @settings(max_examples=5)
    def test_find_parent_no_devtype_mock(self, a_device):
        funcname = "udev_device_get_parent_with_subsystem_devtype"
        spec = lambda d, s, t: None
        with mock.patch.object(
            a_device._libudev, funcname, autospec=spec
        ) as get_parent:
            get_parent.return_value = mock.sentinel.parent_device
            funcname = "udev_device_ref"
            spec = lambda d: None
            with mock.patch.object(
                a_device._libudev, funcname, autospec=spec
            ) as device_ref:
                device_ref.return_value = mock.sentinel.referenced_device
                parent = a_device.find_parent("subsystem")
                assert isinstance(parent, Device)
                assert parent._as_parameter_ is mock.sentinel.referenced_device
                get_parent.assert_called_once_with(a_device, b"subsystem", None)
                device_ref.assert_called_once_with(mock.sentinel.parent_device)

    @given(strategies.sampled_from(_DEVICES))
    @settings(max_examples=5)
    def test_find_parent_with_devtype_mock(self, a_device):
        funcname = "udev_device_get_parent_with_subsystem_devtype"
        spec = lambda d, s, t: None
        with mock.patch.object(
            a_device._libudev, funcname, autospec=spec
        ) as get_parent:
            get_parent.return_value = mock.sentinel.parent_device
            funcname = "udev_device_ref"
            spec = lambda d: None
            with mock.patch.object(
                a_device._libudev, funcname, autospec=spec
            ) as device_ref:
                device_ref.return_value = mock.sentinel.referenced_device
                parent = a_device.find_parent("subsystem", "devtype")
                assert isinstance(parent, Device)
                assert parent._as_parameter_ is mock.sentinel.referenced_device
                get_parent.assert_called_once_with(a_device, b"subsystem", b"devtype")
                device_ref.assert_called_once_with(mock.sentinel.parent_device)

    @given(strategies.sampled_from(_DEVICES))
    @settings(max_examples=5)
    def test_traverse(self, a_device):
        child = a_device
        for parent in pytest.deprecated_call(a_device.traverse):
            assert parent == child.parent
            child = parent

    @given(_CONTEXT_STRATEGY, strategies.sampled_from(_DEVICE_DATA))
    @settings(max_examples=5)
    def test_sys_path(self, a_context, device_datum):
        device = Devices.from_path(a_context, device_datum.device_path)
        assert device.sys_path == device_datum.sys_path
        assert is_unicode_string(device.sys_path)

    @given(_CONTEXT_STRATEGY, strategies.sampled_from(_DEVICE_DATA))
    @settings(max_examples=5)
    def test_device_path(self, a_context, device_datum):
        device = Devices.from_path(a_context, device_datum.device_path)
        assert device.device_path == device_datum.device_path
        assert is_unicode_string(device.device_path)

    @given(_CONTEXT_STRATEGY, strategies.sampled_from(_DEVICE_DATA))
    @settings(max_examples=5)
    def test_subsystem(self, a_context, device_datum):
        device = Devices.from_path(a_context, device_datum.device_path)
        assert device.subsystem == device_datum.properties["SUBSYSTEM"]
        assert is_unicode_string(device.subsystem)

    @given(strategies.sampled_from(_DEVICES))
    @settings(max_examples=5)
    def test_device_sys_name(self, a_device):
        assert a_device.sys_name.replace("/", "!") == os.path.basename(
            a_device.device_path
        )
        assert is_unicode_string(a_device.sys_name)

    @given(strategies.sampled_from(_DEVICES))
    @settings(max_examples=5)
    def test_sys_number(self, a_device):
        match = re.search(r"\d+$", a_device.sys_name)
        # filter out devices with completely nummeric names (first character
        # doesn't count according to the implementation of libudev)
        if match and match.start() > 1:
            assert a_device.sys_number == match.group(0)
            assert is_unicode_string(a_device.sys_name)
        else:
            assert a_device.sys_number is None

    @given(_CONTEXT_STRATEGY, strategies.sampled_from(_DEVICE_DATA))
    @settings(max_examples=5)
    def test_type(self, a_context, device_datum):
        device = Devices.from_path(a_context, device_datum.device_path)
        assert device.device_type == device_datum.properties.get("DEVTYPE")
        if device.device_type:
            assert is_unicode_string(device.device_type)

    @given(_CONTEXT_STRATEGY, strategies.sampled_from(_DEVICE_DATA))
    @settings(max_examples=5)
    def test_driver(self, a_context, device_datum):
        device = Devices.from_path(a_context, device_datum.device_path)
        assert device.driver == device_datum.properties.get("DRIVER")
        if device.driver:
            assert is_unicode_string(device.driver)

    @given(_CONTEXT_STRATEGY, strategies.sampled_from(_DEVICE_DATA))
    @settings(max_examples=5)
    def test_device_node(self, a_context, device_datum):
        device = Devices.from_path(a_context, device_datum.device_path)
        assert device.device_node == device_datum.device_node
        if device.device_node:
            assert is_unicode_string(device.device_node)

    @given(_CONTEXT_STRATEGY, strategies.sampled_from(_DEVICE_DATA))
    @settings(max_examples=5)
    def test_device_number(self, a_context, device_datum):
        device = Devices.from_path(a_context, device_datum.device_path)
        assert device.device_number == device_datum.device_number

    @_UDEV_TEST(165, "test_is_initialized")
    @given(strategies.sampled_from(_DEVICES))
    @settings(max_examples=5)
    def test_is_initialized(self, a_device):
        assert isinstance(a_device.is_initialized, bool)

    @_UDEV_TEST(165, "test_is_initialized_mock")
    @given(strategies.sampled_from(_DEVICES))
    @settings(max_examples=5)
    def test_is_initialized_mock(self, a_device):
        funcname = "udev_device_get_is_initialized"
        spec = lambda d: None
        with mock.patch.object(a_device._libudev, funcname, autospec=spec) as func:
            func.return_value = False
            assert not a_device.is_initialized
            func.assert_called_once_with(a_device)

    @_UDEV_TEST(165, "test_time_since_initialized")
    @given(strategies.sampled_from(_DEVICES))
    @settings(max_examples=5)
    def test_time_since_initialized(self, a_device):
        assert isinstance(a_device.time_since_initialized, timedelta)

    @_UDEV_TEST(165, "test_time_since_initialized_mock")
    @given(strategies.sampled_from(_DEVICES))
    @settings(max_examples=5)
    def test_time_since_initialized_mock(self, a_device):
        funcname = "udev_device_get_usec_since_initialized"
        spec = lambda d: None
        with mock.patch.object(a_device._libudev, funcname, autospec=spec) as func:
            func.return_value = 100
            assert a_device.time_since_initialized.microseconds == 100
            func.assert_called_once_with(a_device)

    @given(_CONTEXT_STRATEGY, strategies.sampled_from(_DEVICE_DATA))
    @settings(max_examples=5)
    def test_links(self, a_context, device_datum):
        device = Devices.from_path(a_context, device_datum.device_path)
        assert sorted(device.device_links) == sorted(device_datum.device_links)
        for link in device.device_links:
            assert is_unicode_string(link)

    @given(strategies.sampled_from(_DEVICES))
    @settings(max_examples=5)
    def test_action(self, a_device):
        assert a_device.action is None

    @given(strategies.sampled_from(_DEVICES))
    @settings(max_examples=5)
    def test_action_mock(self, a_device):
        funcname = "udev_device_get_action"
        spec = lambda d: None
        with mock.patch.object(a_device._libudev, funcname, autospec=spec) as func:
            func.return_value = b"spam"
            assert a_device.action == "spam"
            func.assert_called_once_with(a_device)
            func.reset_mock()
            assert is_unicode_string(a_device.action)
            func.assert_called_once_with(a_device)

    @given(strategies.sampled_from(_DEVICES))
    @settings(max_examples=5)
    def test_sequence_number(self, a_device):
        assert a_device.sequence_number == 0

    @given(strategies.sampled_from(_DEVICES))
    @settings(max_examples=5)
    def test_attributes(self, a_device):
        # see TestAttributes for complete attribute tests
        assert isinstance(a_device.attributes, Attributes)

    def test_no_leak(self):
        """
        Regression test for issue #32, modelled after the script which revealed
        this issue.

        The leak was caused by the following reference cycle between
        ``Attributes`` and ``Device``:

        Device._attributes -> Attributes.device

        https://github.com/lunaryorn/pyudev/issues/32
        """
        for _ in _CONTEXT.list_devices(subsystem="usb"):
            pass
        # make sure that no memory leaks
        assert not gc.garbage

    @given(strategies.sampled_from(_DEVICES))
    @settings(max_examples=5)
    def test_tags(self, a_device):
        # see TestTags for complete tag tests
        assert isinstance(a_device.tags, Tags)

    @given(_CONTEXT_STRATEGY, strategies.sampled_from(_DEVICE_DATA))
    @settings(max_examples=5)
    def test_iteration(self, a_context, device_datum):
        device = Devices.from_path(a_context, device_datum.device_path)
        for prop in device.properties:
            assert is_unicode_string(prop)
        # test that iteration really yields all properties
        device_properties = set(device.properties)
        for prop in device_datum.properties:
            assert prop in device_properties

    @given(_CONTEXT_STRATEGY, strategies.sampled_from(_DEVICE_DATA))
    @settings(max_examples=100)
    @_UDEV_TEST(230, "check exact equivalence of device_datum and device")
    def test_length(self, a_context, device_datum):
        """
        Verify that the keys in the device and in the datum are equal.
        """
        device = Devices.from_path(a_context, device_datum.device_path)
        assert frozenset(device_datum.properties.keys()) == frozenset(
            device.properties.keys()
        )

    @given(_CONTEXT_STRATEGY, strategies.sampled_from(_DEVICE_DATA))
    @settings(max_examples=100)
    def test_key_subset(self, a_context, device_datum):
        """
        Verify that the device contains all the keys in the device datum.
        """
        device = Devices.from_path(a_context, device_datum.device_path)
        assert frozenset(device_datum.properties.keys()) <= frozenset(
            device.properties.keys()
        )

    @given(_CONTEXT_STRATEGY, strategies.sampled_from(_DEVICE_DATA))
    @settings(max_examples=1)
    def test_getitem(self, a_context, device_datum):
        device = Devices.from_path(a_context, device_datum.device_path)
        for prop in device_datum.properties:
            if prop == "DEVLINKS":
                assert sorted(device.properties[prop].split(),) == sorted(
                    device_datum.properties[prop].split(),
                )
            elif prop == "TAGS":
                assert sorted(device.properties[prop].split(":"),) == sorted(
                    device_datum.properties[prop].split(":"),
                )
            else:
                # Do not test equality of device properties with udevadm oracle.
                # https://bugzilla.redhat.com/show_bug.cgi?id=1787089
                pass

    _device_data = [d for d in _DEVICE_DATA if "DEVNAME" in d.properties]

    @pytest.mark.skipif(
        len(_device_data) == 0, reason="no device with a DEVNAME property"
    )
    @given(_CONTEXT_STRATEGY, strategies.sampled_from(_device_data))
    @settings(max_examples=5)
    def test_getitem_devname(self, a_context, device_datum):
        device = Devices.from_path(a_context, device_datum.device_path)
        data_devname = os.path.join(
            a_context.device_path, device_datum.properties["DEVNAME"]
        )
        device_devname = os.path.join(
            a_context.device_path, device.properties["DEVNAME"]
        )
        assert device_devname == data_devname

    @given(strategies.sampled_from(_DEVICES))
    @settings(max_examples=5)
    def test_getitem_nonexisting(self, a_device):
        with pytest.raises(KeyError) as excinfo:
            # pylint: disable=pointless-statement
            a_device.properties["a non-existing property"]
        assert str(excinfo.value) == repr("a non-existing property")

    @given(_CONTEXT_STRATEGY, strategies.sampled_from(_DEVICE_DATA))
    @settings(max_examples=5)
    def test_asint(self, a_context, device_datum):
        device = Devices.from_path(a_context, device_datum.device_path)
        for prop, value in device_datum.properties.items():
            try:
                value = int(value)
            except ValueError:
                with pytest.raises(ValueError):
                    device.properties.asint(prop)
            else:
                assert device.properties.asint(prop) == value

    @given(_CONTEXT_STRATEGY, strategies.sampled_from(_DEVICE_DATA))
    @settings(max_examples=5)
    def test_asbool(self, a_context, device_datum):
        """
        Test that values of 1 and 0 get properly interpreted as bool
        and that all other values raise a ValueError.

        :param Context a_context: libudev context
        :param device_datum: a device datum
        """
        device = Devices.from_path(a_context, device_datum.device_path)
        for prop, value in device_datum.properties.items():
            if value == "1":
                assert device.properties.asbool(prop)
            elif value == "0":
                assert not device.properties.asbool(prop)
            else:
                with pytest.raises(ValueError) as exc_info:
                    device.properties.asbool(prop)

    @given(strategies.sampled_from(_DEVICES))
    @settings(max_examples=5)
    def test_hash(self, a_device):
        assert hash(a_device) == hash(a_device.device_path)
        assert hash(a_device.parent) == hash(a_device.parent)
        assert hash(a_device.parent) != hash(a_device)

    @given(strategies.sampled_from(_DEVICES))
    @settings(max_examples=5)
    def test_equality(self, a_device):
        assert a_device == a_device.device_path
        assert a_device == a_device
        assert a_device.parent == a_device.parent
        # pylint: disable=superfluous-parens
        assert not (a_device == a_device.parent)

    @given(strategies.sampled_from(_DEVICES))
    @settings(max_examples=5)
    def test_inequality(self, a_device):
        # pylint: disable=superfluous-parens
        assert not (a_device != a_device.device_path)
        assert not (a_device != a_device)
        assert not (a_device.parent != a_device.parent)
        assert a_device != a_device.parent

    @given(strategies.sampled_from(_DEVICES))
    @settings(max_examples=1)
    def test_device_ordering(self, a_device):
        """
        Verify that devices are incomparable.
        """
        operators = [operator.ge, operator.gt, operator.le, operator.lt]
        for comp_op in operators:
            with pytest.raises(TypeError) as exc_info:
                comp_op(a_device, a_device)
            assert str(exc_info.value) == "Device not orderable"

    _devices = [
        d
        for d in _DEVICES
        if d.device_type == "disk"
        and "ID_WWN_WITH_EXTENSION" in d.properties
        and "DM_MULTIPATH_TIMESTAMP" not in d.properties
    ]

    @pytest.mark.skipif(
        len(_devices) == 0, reason="unsafe to check ID_WWN_WITH_EXTENSION"
    )
    @given(strategies.sampled_from(_devices))
    @settings(max_examples=5)
    def test_id_wwn_with_extension(self, a_device):
        """
        Test that the ID_WWN_WITH_EXTENSION has a corresponding link.

        Assert that the device is a block device if it has an
        ID_WWN_WITH_EXTENSION property.

        Skip any multipathed paths, see:
        https://bugzilla.redhat.com/show_bug.cgi?id=1263441.
        """
        id_wwn = a_device.properties["ID_WWN_WITH_EXTENSION"]
        assert a_device.subsystem == "block"

        id_path = "/dev/disk/by-id"
        link_name = "wwn-%s" % id_wwn
        match = next((d for d in os.listdir(id_path) if d == link_name), None)
        assert match is not None

        link_path = os.path.join(id_path, match)
        link_target = os.readlink(link_path)
        target_path = os.path.normpath(os.path.join(id_path, link_target))
        assert target_path == a_device.device_node
