# -*- coding: utf-8 -*-
# Copyright (C) 2015 Anne Mulhern <amulhern@redhat.com>

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
    tests.test_conversion
    =====================

    Test converting from values to Python types.

    .. moduleauthor:: mulhern <amulhern@redhat.com>
"""


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from hypothesis import given
from hypothesis import strategies
from hypothesis import Settings

import pytest

from pyudev import ConversionError
from pyudev import Devices
from pyudev import SysfsConversion
from pyudev import SysfsConversions
from pyudev import UdevConversion
from pyudev import UdevConversions

from ._constants import _CONTEXT_STRATEGY
from ._constants import _DEVICE_DATA
from ._constants import _DEVICES
from ._constants import non_volatile_attributes


class TestUdevConversion(object):
    """
    Test simple udev conversions.
    """
    # pylint: disable=too-few-public-methods

    def test_bad_conversions(self):
        """
        Test bad value.
        """
        with pytest.raises(ConversionError):
            UdevConversion.convert(u'1', None)
        with pytest.raises(ConversionError):
            UdevConversion.convert(u'so', UdevConversions.to_int)
        with pytest.raises(ConversionError):
            UdevConversion.convert(u'true', UdevConversions.to_bool)


class TestSysfsConversion(object):
    """
    Test simple sysfs attribute conversions.
    """
    # pylint: disable=too-few-public-methods

    def test_bad_conversions(self):
        """
        Test bad value.
        """
        with pytest.raises(ConversionError):
            SysfsConversion.convert(u'1', None)
        with pytest.raises(ConversionError):
            SysfsConversion.convert(u'so', SysfsConversions.to_int)
        with pytest.raises(ConversionError):
            SysfsConversion.convert(u'true', SysfsConversions.to_bool)


class TestUdevEquivalence(object):
    """
    Test that converting using conversion methods works like instance methods.
    """
    # pylint: disable=too-few-public-methods

    @given(
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=30)
    )
    def test_int_conversion(self, a_device):
        """
        Test conversion to an expected int.
        """
        for prop in a_device:
            try:
                old = a_device.asint(prop)
            except KeyError:
                with pytest.raises(KeyError):
                    # pylint: disable=pointless-statement
                    a_device[prop]
            except ValueError as old_err:
                with pytest.raises(ConversionError) as new_err:
                    UdevConversion.convert(
                       a_device[prop],
                       UdevConversions.to_int
                    )
                    assert new_err.message == old_err
            else:
                new = UdevConversion.convert(
                   a_device[prop],
                   UdevConversions.to_int
                )
                assert old == new

    @given(
       strategies.sampled_from(_DEVICES),
       settings=Settings(max_examples=30)
    )
    def test_bool_conversion(self, a_device):
        """
        Test conversion to an expected bool.
        """
        for prop in a_device:
            try:
                old = a_device.asbool(prop)
            except KeyError:
                with pytest.raises(KeyError):
                    # pylint: disable=pointless-statement
                    a_device[prop]
            except ValueError as old_err:
                with pytest.raises(ConversionError) as new_err:
                    UdevConversion.convert(
                       a_device[prop],
                       UdevConversions.to_bool
                    )
                    assert new_err.message == old_err
            else:
                new = UdevConversion.convert(
                   a_device[prop],
                   UdevConversions.to_bool
                )
                assert old == new


class TestSysfsEquivalence(object):
    """
    Test that converting using conversion methods works like instance methods.
    """

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=30)
    )
    def test_string_conversion(self, a_context, device_datum):
        """
        Test conversion to an expected unicode string.
        """
        device = Devices.from_path(a_context, device_datum.device_path)
        for key, _ in non_volatile_attributes(device_datum.attributes):
            try:
                old = device.attributes.asstring(key)
            except KeyError:
                with pytest.raises(KeyError):
                    # pylint: disable=pointless-statement
                    assert device.attributes.get(key) is None
            except UnicodeDecodeError as old_err:
                with pytest.raises(ConversionError) as new_err:
                    SysfsConversion.convert(
                       device.attributes.get(key),
                       SysfsConversions.to_unicode
                    )
                    assert new_err.message == old_err
            else:
                new = SysfsConversion.convert(
                   device.attributes.get(key),
                   SysfsConversions.to_unicode
                )
                assert old == new

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=30)
    )
    def test_int_conversion(self, a_context, device_datum):
        """
        Test conversion to an expected int.
        """
        device = Devices.from_path(a_context, device_datum.device_path)
        for key, _ in non_volatile_attributes(device_datum.attributes):
            try:
                old = device.attributes.asint(key)
            except KeyError:
                with pytest.raises(KeyError):
                    # pylint: disable=pointless-statement
                    assert device.attributes.get(key) is None
            except (UnicodeDecodeError, ValueError) as old_err:
                with pytest.raises(ConversionError) as new_err:
                    SysfsConversion.convert(
                       device.attributes.get(key),
                       SysfsConversions.to_int
                    )
                    assert new_err.message == old_err
            else:
                new = SysfsConversion.convert(
                   device.attributes.get(key),
                   SysfsConversions.to_int
                )
                assert old == new

    @given(
       _CONTEXT_STRATEGY,
       strategies.sampled_from(_DEVICE_DATA),
       settings=Settings(max_examples=50)
    )
    def test_bool_conversion(self, a_context, device_datum):
        """
        Test conversion to an expected bool.
        """
        device = Devices.from_path(a_context, device_datum.device_path)
        for key, _ in non_volatile_attributes(device_datum.attributes):
            try:
                old = device.attributes.asbool(key)
            except KeyError:
                with pytest.raises(KeyError):
                    # pylint: disable=pointless-statement
                    assert device.attributes.get(key) is None
            except (UnicodeDecodeError, ValueError) as old_err:
                with pytest.raises(ConversionError) as new_err:
                    SysfsConversion.convert(
                       device.attributes.get(key),
                       SysfsConversions.to_bool
                    )
                    assert new_err.message == old_err
            else:
                new = SysfsConversion.convert(
                   device.attributes.get(key),
                   SysfsConversions.to_bool
                )
                assert old == new
