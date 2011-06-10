#!/usr/bin/python2
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Sebastian Wiesner <lunaryorn@googlemail.com>

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
    binding_coverage
    ================

    Check binding coverage.  Needs gccxml and lxml.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""


from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import os
from tempfile import NamedTemporaryFile
from subprocess import check_call

from lxml import etree

from pyudev._libudev import SIGNATURES

STANDARD_INCLUDE_PATH = '/usr/include/'

# a list of functions, which is not going to be wrapped
BLACKLIST = frozenset([
     # vararg functions not supported by ctypes
    'udev_set_log_fn',
    # superfluous in Python, because arbitrary attributes can be attached to
    # objects anyways
    'udev_set_userdata', 'udev_get_userdata',
    # superfluous, because context is already available in .context
    'udev_enumerate_get_udev', 'udev_monitor_get_udev',
    # superfluous, because Python provides already tools to filter lists
    'udev_device_get_udev', 'udev_list_entry_get_by_name',
    # undocumented in libudev manual
    'udev_device_get_seqnum'
])


def find_libudev_h():
    return os.path.join(STANDARD_INCLUDE_PATH, 'libudev.h')


def parse_libudev_h():
    libudev_h_file = find_libudev_h()
    with NamedTemporaryFile() as stream:
        check_call(['gccxml', libudev_h_file, '-fxml={0}'.format(stream.name)])
        return etree.parse(stream.name)


def get_libudev_functions():
    xml_ast = parse_libudev_h()
    function_names = xml_ast.xpath('//Function/@name')
    return [f for f in function_names if f.startswith('udev_')]


def wrapped_functions():
    return ('{0}_{1}'.format(namespace, member)
            for namespace, members in SIGNATURES.iteritems()
            for member in members)

def main():
    all_functions = set(get_libudev_functions())
    unwrapped_functions = all_functions.difference(
        wrapped_functions(), BLACKLIST)
    print('\n'.join(sorted(unwrapped_functions)))


if __name__ == '__main__':
    main()
