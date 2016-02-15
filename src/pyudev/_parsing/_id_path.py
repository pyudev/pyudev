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


class IdPathField(Field):
    """
    Overrides default regular expression.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, name, regexp=r'[^-]+', description=None):
        super(IdPathField, self).__init__(name, regexp, description)


class IdPathParsers(object):
    """
    Aggregate parsers.
    """
    # pylint: disable=too-few-public-methods

    PARSERS = [
       Parser(r'acpi-%s', [IdPathField('sys_name')]),
       Parser(r'ap-%s', [IdPathField('sys_name')]),
       Parser(r'ata-%s', [IdPathField('port_no')]),
       Parser(r'bcma-%s', [IdPathField('core')]),
       Parser(r'cciss-disk%s', [IdPathField('disk')]),
       Parser(r'ccw-%s', [IdPathField('sys_name')]),
       Parser(r'ccwgroup-%s', [IdPathField('sys_name')]),
       Parser(r'fc-%s-%s', [IdPathField('port_name'), IdPathField('lun')]),
       Parser(
          r'ip-%s:%s-iscsi-%s-%s',
          [
             IdPathField('persistent_address'),
             IdPathField('persistent_port'),
             IdPathField('target_name'),
             IdPathField('lun')
          ]
       ),
       Parser(r'iucv-%s', [IdPathField('sys_name')]),
       Parser(r'nst%s', [IdPathField('name')]),
       Parser(r'pci-%s', [IdPathField('sys_name')]),
       Parser(r'platform-%s', [IdPathField('sys_name')]),
       Parser(r'sas-%s-lun-%s',
          [IdPathField('sas_address'), IdPathField('lun')]
       ),
       Parser(
          r'sas-exp%s-phy%s-%s',
          [
             IdPathField(
                'sas_address',
                r'.*',
                'sysfs sas_address attribute of expander'
             ),
             IdPathField(
                'phy_identifier',
                r'.*',
                'sysfs phy_identifier attribute of target sas device'
             ),
             IdPathField('lun', description='sysnum of device (0 if none)')
          ]
       ),
       Parser(
          r'sas-phy%s-%s',
          [
             IdPathField(
                'phy_identifier',
                r'.*',
                'sysfs phy_identifier attribute of target sas device'
             ),
             IdPathField('lun', description='sysnum of device (0 if none)')
          ]
       ),
       Parser(r'scm-%s', [IdPathField('sys_name')]),
       Parser(
          r'scsi-%s:%s:%s:%s',
          [
             IdPathField('host'),
             IdPathField('bus'),
             IdPathField('target'),
             IdPathField('lun')
          ]
       ),
       Parser('serio-%s', [IdPathField('sysnum')]),
       Parser('st%s', [IdPathField('name')]),
       Parser('usb-0:%s', [IdPathField('port')]),
       Parser('virtio-pci-%s', [IdPathField('sys_name')]),
       Parser('vmbus-%s-%s', [IdPathField('guid'), IdPathField('lun')]),
       Parser('xen-%s', [IdPathField('sys_name')])
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
            value = value[len(best_match.group('total')) + 1:]

        return match_list
