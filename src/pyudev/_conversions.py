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
    pyudev._conversions
    ===================

    Converting from string values to Python types.

    .. moduleauthor:: mulhern <amulhern@redhat.com>
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc

from six import add_metaclass

from ._util import ensure_unicode_string
from ._util import string_to_bool

__all__ = [
   'ConversionError',
   'SysfsConversion',
   'SysfsConversions',
   'UdevConversion',
   'UdevConversions'
]

@add_metaclass(abc.ABCMeta)
class Conversion(object):
    """
    Parent class for conversion types.
    """
    # pylint: disable=too-few-public-methods

    def __str__(self): # pragma: no cover
        return self.__class__.__name__
    __repr__ = __str__

    def __deepcopy__(self, memo): # pragma: no cover
        # pylint: disable=unused-argument
        return self

    def __copy__(self): # pragma: no cover
        return self

class TO_BOOL(Conversion): # pylint: disable=invalid-name
    """
    To bool.
    """
    # pylint: disable=too-few-public-methods

    pass

TO_BOOL = TO_BOOL()

class TO_INT(Conversion): # pylint: disable=invalid-name
    """
    To int.
    """
    # pylint: disable=too-few-public-methods

    pass

TO_INT = TO_INT()

class TO_UNICODE(Conversion): # pylint: disable=invalid-name
    """
    To unicode.
    """
    # pylint: disable=too-few-public-methods

    pass

TO_UNICODE = TO_UNICODE()

class SysfsConversions(object):
    """
    Available sysfs conversions.
    """
    # pylint: disable=too-few-public-methods

    to_bool = TO_BOOL
    to_int = TO_INT
    to_unicode = TO_UNICODE


class UdevConversions(object):
    """
    Available udev conversions.
    """
    # pylint: disable=too-few-public-methods

    to_bool = TO_BOOL
    to_int = TO_INT

class ConversionError(Exception):
    """
    Abstract superclass of conversion errors.
    """
    pass

class UnknownConversionTypeError(ConversionError):
    """
    Raised if an unknown conversion type is specified.
    """
    pass

class ConversionFailureError(ConversionError):
    """
    Raised if a conversion is attempted and there is some failure.
    """
    pass

class SysfsConversion(object):
    """
    Converting from sysfs attributes.

    Sysfs attributes can be arbitrary bytes, so conversion to unicode may fail.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def convert(value, conversion=SysfsConversions.to_unicode):
        """
        Convert the value, a sysfs attribute, according to conversion.

        :param value: the value to convert
        :type value: bytes or unicode
        :param Conversion conversion: what conversion to do
        :returns: a value of the correct type
        :rtype: the type specified by ``conversion``
        """

        try:
            if conversion is SysfsConversions.to_unicode:
                return ensure_unicode_string(value)
            if conversion is SysfsConversions.to_bool:
                return string_to_bool(ensure_unicode_string(value))
            if conversion is SysfsConversions.to_int:
                return int(ensure_unicode_string(value))
            raise UnknownConversionTypeError(conversion)
        except (ValueError, UnicodeDecodeError) as err:
            raise ConversionFailureError(err)


class UdevConversion(object):
    """
    Converting from udev properties.

    pyudev implicitly converts udev properties to unicode, so no
    conversion to unicode available for udev properties.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def convert(value, conversion):
        """
        Convert the value, a sysfs attribute, according to conversion.

        :param value: the value to convert
        :type value: unicode
        :param Conversion conversion: what conversion to do
        :returns: a value of the correct type
        :rtype: the type specified by ``conversion``
        """

        try:
            if conversion is UdevConversions.to_bool:
                return string_to_bool(value)
            if conversion is UdevConversions.to_int:
                return int(value)
            raise UnknownConversionTypeError(conversion)
        except ValueError as err:
            raise ConversionFailureError(err)
