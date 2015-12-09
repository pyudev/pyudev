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

import pytest

import pyudev

from pyudev import ConversionError
from pyudev import SysfsConversion
from pyudev import SysfsConversions
from pyudev import UdevConversion
from pyudev import UdevConversions


class TestUdevConversion(object):
    """
    Test simple udev conversions.
    """

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
