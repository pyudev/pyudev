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
    pyudev._parsing._shared
    =======================

    Some classes that parsers share.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import re


class Parser(object):
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


class Field(object):
    """
    A field in an id_path.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, name, regexp=r'.*', description=None):
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
