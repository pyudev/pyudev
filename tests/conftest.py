# -*- coding: utf-8 -*-
# Copyright (C) 2010, 2011, 2012 Sebastian Wiesner <lunaryorn@googlemail.com>

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

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import select
from contextlib import closing

import sys
import os
import re
import random
import subprocess
import socket
import errno
from functools import wraps
from collections import namedtuple
from contextlib import contextmanager
from subprocess import call
if sys.version_info[:2] < (3, 2):
    from contextlib import nested

import mock
import pytest

import pyudev


pytest_plugins = [
    str('tests.plugins.udev_database'),
    str('tests.plugins.fake_monitor'),
    str('tests.plugins.privileged')
]


if sys.version_info[:2] >= (3, 2):
    @contextmanager
    def nested(*managers):
        """
        Copy of contextlib.nested from python 2.7 with slight adaptions to
        Python 3.2 to use nested() on python 3.2 and thus retain backwards
        compatibility with Python 2.6 (with doesn't support the new nesting
        syntax), while being able to run the test suite on Python 3.2 as
        well (which doesn't provide contextlib.nested anymore).
        """
        exits = []
        vars = []
        exc = None
        try:
            for mgr in managers:
                exit = mgr.__exit__
                enter = mgr.__enter__
                vars.append(enter())
                exits.append(exit)
            yield vars
        except BaseException as e:
            exc = e
        finally:
            while exits:
                exit = exits.pop()
                try:
                    if exc:
                        args = (type(exc), exc, exc.__traceback__)
                    else:
                        args = (None, None, None)
                    if exit(*args):
                        exc = None
                except BaseException as e:
                    exc = e
            if exc:
                raise exc


def assert_env_error(error, errno, filename=None):
    __tracebackhide__ = True
    assert error.errno == errno
    assert error.strerror == os.strerror(errno)
    assert error.filename == filename


@contextmanager
def patch_libudev(funcname):
    with mock.patch('pyudev._libudev.libudev.{0}'.format(funcname)) as func:
        yield func


class Node(namedtuple('Node', 'name next')):
    """
    Node in a :class:`LinkedList`.
    """
    @property
    def value(self):
        return 'value of {0}'.format(self.name)


class LinkedList(object):
    """
    Linked list class to mock libudev list functions.
    """

    @classmethod
    def from_sequence(cls, items):
        next_node = None
        for item in reversed(items):
            node = Node(item, next_node)
            next_node = node
        return cls(next_node)

    def __init__(self, first):
        self.first = first


@contextmanager
def patch_libudev_list(items, list_func):
    linked_list = LinkedList.from_sequence(items)
    get_next = 'udev_list_entry_get_next'
    get_name = 'udev_list_entry_get_name'
    get_value = 'udev_list_entry_get_value'
    with pytest.nested(pytest.patch_libudev(get_next),
                       pytest.patch_libudev(get_name),
                       pytest.patch_libudev(get_value),
                       pytest.patch_libudev(list_func)) as (get_next, get_name,
                                                            get_value,
                                                            list_func):
        list_func.return_value = linked_list.first
        get_name.side_effect = lambda e: e.name
        get_value.side_effect = lambda e: e.value
        get_next.side_effect = lambda e: e.next
        yield list_func


def is_unicode_string(value):
    """
    Return ``True``, if ``value`` is of a real unicode string type
    (``unicode`` in python 2, ``str`` in python 3), ``False`` otherwise.
    """
    if sys.version_info[0] >= 3:
        unicode_type = str
    else:
        unicode_type = unicode
    return isinstance(value, unicode_type)


def pytest_namespace():
    return dict((func.__name__, func) for func in
                (patch_libudev, nested, is_unicode_string,
                 patch_libudev_list, assert_env_error))


def pytest_funcarg__context(request):
    """
    Return a useable :class:`pyudev.Context` object.  The context is cached
    with session scope.
    """
    return request.cached_setup(setup=pyudev.Context, scope='session')


def pytest_funcarg__device_path(request):
    """
    Return a device path as string.

    The device path must be available as ``request.param``.
    """
    return request.param


def pytest_funcarg__all_properties(request):
    """
    Get all properties from the exported database (as returned by the
    ``database`` funcarg) of the device pointed to by the ``device_path``
    funcarg.
    """
    device_path = request.getfuncargvalue('device_path')
    database = request.getfuncargvalue('udev_database')
    return database.get_device_properties(device_path)


def pytest_funcarg__properties(request):
    """
    Same as the ``all_properties`` funcarg, but with the special ``DEVNAME``
    property removed.
    """
    properties = request.getfuncargvalue('all_properties')
    properties.pop('DEVNAME', None)
    return properties


def pytest_funcarg__tags(request):
    """
    Return the tags of the device pointed to by the ``device_path`` funcarg.
    """
    device_path = request.getfuncargvalue('device_path')
    database = request.getfuncargvalue('udev_database')
    return database.get_device_tags(device_path)


def pytest_funcarg__attributes(request):
    """

    Return a dictionary of all attributes for the device pointed to by the
    ``device_path`` funcarg.
    """
    device_path = request.getfuncargvalue('device_path')
    database = request.getfuncargvalue('udev_database')
    return database.get_device_attributes(device_path)


def pytest_funcarg__device_node(request):
    """
    Return the name of the device node for the device pointed to by the
    ``device_path`` funcarg.
    """
    device_path = request.getfuncargvalue('device_path')
    database = request.getfuncargvalue('udev_database')
    return database.get_device_node(device_path)


def pytest_funcarg__device_number(request):
    """
    Return the device number of the device pointed to by the ``device_path``
    funcarg.
    """
    device_path = request.getfuncargvalue('device_path')
    database = request.getfuncargvalue('udev_database')
    return database.get_device_number(device_path)


def pytest_funcarg__device_links(request):
    """
    Return a list of symlink to the device node (``device_node`` funcarg)
    for the device pointed to by the ``device_path`` funcarg.
    """
    device_path = request.getfuncargvalue('device_path')
    database = request.getfuncargvalue('udev_database')
    return database.get_device_links(device_path)


def pytest_funcarg__sys_path(request):
    """
    Return the sys_path including the sysfs mountpoint for the device path
    returned by the ``device_path`` funcarg.
    """
    context = request.getfuncargvalue('context')
    device_path = request.getfuncargvalue('device_path')
    return context.sys_path + device_path


def pytest_funcarg__device(request):
    """
    Create and return a :class:`pyudev.Device` object for the sys_path
    returned by the ``sys_path`` funcarg, and the context from the
    ``context`` funcarg.
    """
    sys_path = request.getfuncargvalue('sys_path')
    context = request.getfuncargvalue('context')
    return pyudev.Device.from_sys_path(context, sys_path)


def pytest_funcarg__platform_device(request):
    """
    Return the platform device at ``/sys/devices/platform``.  This device
    object exists on all systems, and is therefore suited to for testing
    purposes.
    """
    context = request.getfuncargvalue('context')
    return pyudev.Device.from_sys_path(context, '/sys/devices/platform')
