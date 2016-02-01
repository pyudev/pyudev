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

import re

from collections import defaultdict


class _Parser(object):
    """
    A parser for udev ID_PATH values.
    """

    def __init__(self, format_string, fields):
        """
        Initializer.

        :param str format_string: string used to format this id by udev
        :param fields: list of fields that fill the string

        ``format_string`` must content itself with basic C-style format
        codes, beginning with '%' as '%s', '%d'.
        """
        self.format_string = '%s' % format_string
        self.fields = fields
        self._prefix = self.format_string.split('%', 1)[0]

        substitution_list = [
           ('(?P<%s>%s)' % (f.name, f.regexp)) for f in self.fields
        ]
        regexp = self.format_string % tuple(substitution_list)
        self._regexp = re.compile('(?P<total>%s)' % regexp)

    @property
    def regexp(self):
        """
        The regular expression that should match this value.

        :returns: the regular expression that should match this value
        :rtype: compiled regular expression

        The regular expression uses ?P<name> syntax.

        If there is a match, match.groups('total') matches the entire matched
        string.
        """
        return self._regexp

    @property
    def prefix(self):
        """
        A partially distinguishing prefix.

        Some parsers may use the same prefix.

        :returns: a prefix that distinguishes the parser from other parsers
        """
        return self._prefix

    @property
    def keys(self):
        """
        Keys within the regular expression.

        :returns: a list of the keys useful for finding portions of a match
        :rtype: list of str
        """
        return [f.name for f in self.fields]


class _Field(object):
    """
    A field in an id_path.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, name, regexp, description=None):
        """
        Initializer.

        :param str name: the name of the field
        :param str regexp: regular expression to match the field

        The best choice of regular expression may generally define a language
        that is a superset of the actual language of the field.
        Since the containing regular expression will constrain matches, the
        regular expression does not need to be the most precise.
        In general, '.*' may be good enough.
        """
        self.name = name
        self.regexp = regexp
        self.description = description


class IdPathParsers(object):
    """
    Aggregate parsers.
    """
    # pylint: disable=too-few-public-methods

    PARSERS = [
       _Parser('acpi-%s', [_Field('sys_name', '.*')]),
       _Parser('ap-%s', [_Field('sys_name', '.*')]),
       _Parser('ata-%s', [_Field('port_no', '.*')]),
       _Parser('bcma-%s', [_Field('core', '.*')]),
       _Parser('cciss-disk%s', [_Field('disk', '.*')]),
       _Parser('ccw-%s', [_Field('sys_name', '.*')]),
       _Parser('ccwgroup-%s', [_Field('sys_name', '.*')]),
       _Parser('fc-%s-%s', [_Field('port_name', '.*'), _Field('lun', '.*')]),
       _Parser(
          'ip-%s:%s-iscsi-%s-%s',
          [
             _Field('persistent_address', '.*'),
             _Field('persistent_port', '.*'),
             _Field('target_name', '.*'),
             _Field('lun', '.*')
          ]
       ),
       _Parser('iucv-%s', [_Field('sys_name', '.*')]),
       _Parser('nst%s', [_Field('name', '.*')]),
       _Parser('pci-%s', [_Field('sys_name', '.*')]),
       _Parser('platform-%s', [_Field('sys_name', '.*')]),
       _Parser('sas-%s-%s', [_Field('sas_address', '.*'), _Field('lun', '.*')]),
       _Parser(
          'sas-exp%s-phy%s-%s',
          [
             _Field(
                'sas_address',
                '.*',
                'sysfs sas_address attribute of expander'
             ),
             _Field(
                'phy_identifier',
                '.*',
                'sysfs phy_identifier attribute of target sas device'
             ),
             _Field('lun', '.*', 'sysnum of device (0 if none)')
          ]
       ),
       _Parser(
          'sas-phy%s-%s',
          [
             _Field(
                'phy_identifier',
                '.*',
                'sysfs phy_identifier attribute of target sas device'
             ),
             _Field('lun', '.*', 'sysnum of device (0 if none)')
          ]
       ),
       _Parser('scm-%s', [_Field('sys_name', '.*')]),
       _Parser(
          'scsi-%s:%s:%s:%s',
          [
             _Field('host', '.*'),
             _Field('bus', '.*'),
             _Field('target', '.*'),
             _Field('lun', '.*')
          ]
       ),
       _Parser('serio-%s', [_Field('sysnum', '.*')]),
       _Parser('st%s', [_Field('name', '.*')]),
       _Parser('usb-0:%s', [_Field('port', '.*')]),
       _Parser('vmbus-%s-%s', [_Field('guid', '.*'), _Field('lun', '.*')]),
       _Parser('xen-%s', [_Field('sys_name', '.*')])
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
        :type parsers: list of _Parser
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
