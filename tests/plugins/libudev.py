# -*- coding: utf-8 -*-
# Copyright (C) 2012 Sebastian Wiesner <lunaryorn@gmail.com>

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
    plugins.libudev
    ===============

    Provide a list of all libudev functions as declared in ``libudev.h``.

    This plugin parses ``libudev.h`` with :program:`gccxml` and extracts all
    libudev functions from this header.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@gmail.com>
"""


from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from collections import namedtuple
from operator import attrgetter
from tempfile import NamedTemporaryFile
from subprocess import check_call
from xml.etree import cElementTree as etree

import py.path
import pytest


class GCCXMLParser(object):
    """
    The parser to parse translation units.
    """

    @classmethod
    def default_parser(cls):
        """
        Create a default parser.

        This method searches :program:`gccxml` in ``$PATH``.

        Return a :class:`GCCXMLParser`, if :program:`gccxml` is found.  Raise
        :exc:`~exceptions.LookupError` otherwise.
        """
        gccxml = py.path.local.sysfind('gccxml')
        if not gccxml:
            raise LookupError('Could not find "gccxml"')
        return cls(str(gccxml))

    def __init__(self, gccxml):
        self.gccxml = gccxml

    def parse(self, filename):
        # by opening the file in Python and piping it to gccxml we get nice
        # Python exceptions if filename can't be read, instead of mucking
        # around with the gccxml return value.
        with open(filename, 'r') as source:
            with NamedTemporaryFile() as sink:
                cmd = [self.gccxml, '-', '-fxml={0}'.format(sink.name)]
                check_call(cmd, stdin=source)
                return etree.parse(sink.name)


# wrap symbol types required to represent libudev declarations into nice tuples
Function = namedtuple('Function', 'name arguments return_type')
# libudev only uses forward-declared structs, so we can ignore struct members
Struct = namedtuple('Struct', 'name')
FundamentalType = namedtuple('FundamentalType', 'name')
CvQualifiedType = namedtuple('CvQualifiedType', 'type')
PointerType = namedtuple('PointerType', 'type')
Typedef = namedtuple('Typedef', 'type')


class Unit(object):
    """
    A translation unit.

    Parses a translation unit and provides a list of all symbols in this unit.
    """

    @classmethod
    def parse(cls, filename, parser=None):
        """
        Parse the translation unit denoted by ``filename``.

        ``filename`` is a string denoting the file to parse.  ``parser`` is a
        :class:`GCCXMLParser` to use for parsing.  If ``None``,
        :meth:`GCCXMLParser.default_parser()` is used.

        Return a :class:`Unit` representing the parsed unit.  Raise
        :exc:`~exceptions.EnvironmentError`, if ``filename`` could not be
        opened or read.
        """
        if parser is None:
            parser = GCCXMLParser.default_parser()
        tree = parser.parse(filename)
        return cls.from_tree(tree)

    @classmethod
    def from_tree(cls, tree):
        return cls(tree)

    def __init__(self, tree):
        self.tree = tree
        self._symbol_table = {}
        self._symbols = {}

    def _build_symbol_table(self):
        if self._symbol_table:
            return
        for symbol in self.tree.getroot():
            self._symbol_table[symbol.get('id')] = symbol

    def _resolve_Function(self, symbol):
        return_type = self._resolve_symbol(symbol.get('returns'))
        arguments = tuple(self._resolve_symbol(a.get('type'))
                          for a in symbol.findall('./Argument'))
        return Function(symbol.get('name'), arguments, return_type)

    def _resolve_Struct(self, symbol):
        return Struct(symbol.get('name'))

    def _resolve_FundamentalType(self, symbol):
        return FundamentalType(symbol.get('name'))

    def _resolve_CvQualifiedType(self, symbol):
        return CvQualifiedType(self._resolve_symbol(symbol.get('type')))

    def _resolve_PointerType(self, symbol):
        return PointerType(self._resolve_symbol(symbol.get('type')))

    def _resolve_Typedef(self, symbol):
        return Typedef(self._resolve_symbol(symbol.get('type')))

    def _resolve_symbol(self, symbol):
        if not isinstance(symbol, type(self.tree.getroot())):
            symbol = self._symbol_table[symbol]
        symbol_id = symbol.get('id')
        if symbol_id not in self._symbols:
            resolve_func_name = '_resolve_{0}'.format(symbol.tag)
            resolve = getattr(self, resolve_func_name, None)
            self._symbols[symbol_id] = resolve(symbol) if resolve else None
        return self._symbols[symbol_id]

    def _resolve_symbols(self):
        if self._symbols:
            return
        for symbol in self.tree.getroot():
            self._resolve_symbol(symbol)

    @property
    def symbols(self):
        """
        Yield all symbols in this unit.

        .. warning::

           This does not really yield *all* symbols, but only those symbol
           types that are required to parse ``libudev.h``.  Other symbols,
           e.g. C++ classes or namespaces, are ignored.
        """
        self._build_symbol_table()
        self._resolve_symbols()
        return self._symbols.values()

    @property
    def functions(self):
        """
        Yield all functions in this unit as :class:`Function` objects.
        """
        return (s for s in self.symbols if isinstance(s, Function))


LIBUDEV_H = '/usr/include/libudev.h'


def pytest_configure(config):
    try:
        libudev_h = Unit.parse(LIBUDEV_H)
        config.libudev_functions = [f for f in libudev_h.functions
                                    if f.name.startswith('udev_')]
        config.libudev_error = None
    except (EnvironmentError, LookupError) as error:
        config.libudev_functions = []
        config.libudev_error = error


def pytest_generate_tests(metafunc):
    if 'libudev_function' in metafunc.funcargnames:
        functions = sorted(metafunc.config.libudev_functions,
                           key=attrgetter('name'))
        if functions:
            metafunc.parametrize('libudev_function', functions, indirect=True,
                                 ids=[f.name for f in functions])
        else:
            metafunc.parametrize('libudev_function',
                                 [metafunc.config.libudev_error],
                                 indirect=True)


def pytest_funcarg__libudev_function(request):
    """
    Return each :class:`Function` parsed from libudev.

    If libudev could not be parsed, the invoking test is skipped.
    """
    if isinstance(request.param, Function):
        return request.param
    else:
        pytest.skip(str(request.param))
