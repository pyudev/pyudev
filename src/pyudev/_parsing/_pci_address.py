# -*- coding: utf-8 -*-
# Copyright (C) 2016 mulhern <amulhern@redhat.com>

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
    pyudev._parsing._pci_address
    ============================

    Parsing a PCI address.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from ._shared import Field
from ._shared import Parser


class PCIAddressParse(object):
    """
    Parse a pci address.
    """
    # pylint: disable=too-few-public-methods

    _PARSER = Parser(
       r'%s:%s:%s\.%s',
       [
          Field('domain', description='range 256'),
          Field('bus', description='range 256'),
          Field('device', description='range 32'),
          Field('function', description='range 8')
       ]
    )

    def parse(self, value):
        """
        Parse the value.

        :param str value: the value to parse
        :returns: the result of parsing
        :rtype: Parser * (Match or NoneType)
        """
        return (self._PARSER, self._PARSER.regexp.match(value))
