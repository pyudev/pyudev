# -*- coding: utf-8 -*-
# Copyright (C) 2016 Anne Mulhern <amulhern@redhat.com>

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
    pyudev.device._dm_uuid
    ======================

    Parsing DM_UUID values.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ._shared import Field
from ._shared import Parser


class DMUUIDParse(object):
    """
    Represents a DM_UUID.
    """
    # pylint: disable=too-few-public-methods

    _PARSER = Parser(
       r'%s-%s',
       [
          Field('subsystem', description='device mapper subsystem'),
          Field('UUID', description="an identifier")
       ]
    )

    def parse(self, value):
        """
        Parse value.

        :returns: tuple of the parser and the parsed object
        :rtype: tuple of Parser * (Match or NoneType)
        """
        return (self._PARSER, self._PARSER.regexp.match(value))
