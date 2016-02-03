# -*- coding: utf-8 -*-
# Copyright (C) 2015 mulhern <amulhern@redhat.com>

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
    pyudev._parsing._id_path
    ========================

    Parsing the ID_PATH udev property.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from collections import defaultdict

from ._shared import Field
from ._shared import Parser


class IdPathParsers(object):
    """
    Aggregate parsers.
    """
    # pylint: disable=too-few-public-methods

    PARSERS = [
       Parser(r'acpi-%s', [Field('sys_name')]),
       Parser(r'ap-%s', [Field('sys_name')]),
       Parser(r'ata-%s', [Field('port_no')]),
       Parser(r'bcma-%s', [Field('core')]),
       Parser(r'cciss-disk%s', [Field('disk')]),
       Parser(r'ccw-%s', [Field('sys_name')]),
       Parser(r'ccwgroup-%s', [Field('sys_name')]),
       Parser(r'fc-%s-%s', [Field('port_name'), Field('lun')]),
       Parser(
          r'ip-%s:%s-iscsi-%s-%s',
          [
             Field('persistent_address'),
             Field('persistent_port'),
             Field('target_name'),
             Field('lun')
          ]
       ),
       Parser(r'iucv-%s', [Field('sys_name')]),
       Parser(r'nst%s', [Field('name')]),
       Parser(r'pci-%s', [Field('sys_name')]),
       Parser(r'platform-%s', [Field('sys_name')]),
       Parser(r'sas-%s-%s', [Field('sas_address'), Field('lun')]),
       Parser(
          r'sas-exp%s-phy%s-%s',
          [
             Field(
                'sas_address',
                r'.*',
                'sysfs sas_address attribute of expander'
             ),
             Field(
                'phy_identifier',
                r'.*',
                'sysfs phy_identifier attribute of target sas device'
             ),
             Field('lun', description='sysnum of device (0 if none)')
          ]
       ),
       Parser(
          r'sas-phy%s-%s',
          [
             Field(
                'phy_identifier',
                r'.*',
                'sysfs phy_identifier attribute of target sas device'
             ),
             Field('lun', description='sysnum of device (0 if none)')
          ]
       ),
       Parser(r'scm-%s', [Field('sys_name')]),
       Parser(
          r'scsi-%s:%s:%s:%s',
          [
             Field('host'),
             Field('bus'),
             Field('target'),
             Field('lun')
          ]
       ),
       Parser('serio-%s', [Field('sysnum')]),
       Parser('st%s', [Field('name')]),
       Parser('usb-0:%s', [Field('port')]),
       Parser('vmbus-%s-%s', [Field('guid'), Field('lun')]),
       Parser('xen-%s', [Field('sys_name')])
    ]


class IdPathParse(object):
    """
    Manage the parsing of an ID_PATH value.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, parsers):
        """
        Initializer.

        :param parsers: parser objects to parse with
        :type parsers: list of Parser
        """
        self.parsers = parsers

        self._table = defaultdict(list)
        for parser in self.parsers:
            self._table[parser.prefix].append(parser)

        self._keys = self._table.keys()

    def _parse_one(self, value):
        """
        Parse the first part of the value.

        :param str value: the value to parse
        :returns: the result of parsing, may be several matches
        :rtype: list of parser * match pairs
        """
        keys = (key for key in self._keys if value.startswith(key))
        parsers = (p for key in keys for p in self._table[key])
        matches = ((p, p.regexp.match(value)) for p in parsers)
        return [(p, m) for (p, m) in matches if m is not None]

    def parse(self, value):
        """
        Parse the value.

        :param str value: the value to parse
        :returns: the result of parsing
        :rtype: list of list of parser * match pairs

        Returns the empty list if parsing fails.

        If multiple matches, picks the match with the longest matching prefix.

        There should not ever be a tie, because, if there are two equally
        long matching prefixes, only one can match.
        """
        match_list = []
        while value != '':
            matches = self._parse_one(value)
            if matches == []:
                return []

            (parser, best_match) = max(matches, key=lambda x: len(x[0].prefix))
            match_list.append((parser, best_match))
            value = value[len(best_match.group('total')):]

        return match_list
