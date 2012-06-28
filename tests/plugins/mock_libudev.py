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
    plugins.mock_libudev
    ====================

    Plugin to mock calls to libudev.

    This plugin adds :func:`calls_to_libudev()` and :func:`libudev_list()` to
    the :mod:`pytest` namespace.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@gmail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from operator import attrgetter
from contextlib import contextmanager
from collections import namedtuple

import mock


@contextmanager
def calls_to_libudev(function_calls):
    """
    Mock libudev functions and check calls to the mocked functions::

       calls = {'udev_device_ref': [(device,)]}
       with pytest.calls_to_libudev(calls):
           device.parent

    ``function_calls`` is a dictionary that maps libudev function names to a
    list of calls, where each call is represented as tuple containing the
    arguments expected to be passed to the function.

    If any call in ``function_calls`` does not occur, the function triggers an
    assertion.

    All mocked functions are restored if the context exits.
    """
    from pyudev._libudev import libudev
    mocks = dict((function, mock.DEFAULT) for function in function_calls)
    with mock.patch.multiple(libudev, **mocks):
        yield
        for name, calls in function_calls.items():
            function = getattr(libudev, name)
            function.assert_has_calls([mock.call(*c) for c in calls])


Node = namedtuple('Node', 'name value next')


class LinkedList(object):
    """
    Linked list class to mock libudev list functions.
    """

    @classmethod
    def from_iterable(cls, iterable):
        """
        Create a list from the given ``iterable``.
        """
        next_node = None
        for item in reversed(iterable):
            if isinstance(item, tuple):
                name, value = item
            else:
                name, value = item, None
            node = Node(name, value, next_node)
            next_node = node
        return cls(next_node)

    def __init__(self, first):
        self.first = first


@contextmanager
def libudev_list(function, items):
    """
    Mock a libudev linked list::

       with pytest.libudev_list('udev_device_get_tag_list_entry', ['foo', 'bar']):
           assert list(device.tags) == ['foo', 'bar']

    ``function`` is a string containing the name of the libudev function that
    returns the list.  ``items`` is an iterable yielding items which shall be
    returned by the mocked list function.  An item in ``items`` can either be a
    tuple with two components, where the first component is the item name, and
    the second the item value, or a single element, which is the item name.
    The item value is ``None`` in this case.
    """
    from pyudev._libudev import libudev
    functions_to_patch = [function, 'udev_list_entry_get_next',
                          'udev_list_entry_get_name',
                          'udev_list_entry_get_value']
    mocks = dict((f, mock.DEFAULT) for f in functions_to_patch)
    with mock.patch.multiple(libudev, **mocks):
        udev_list = LinkedList.from_iterable(items)
        getattr(libudev, function).return_value = udev_list.first
        libudev.udev_list_entry_get_name.side_effect = attrgetter('name')
        libudev.udev_list_entry_get_value.side_effect = attrgetter('value')
        libudev.udev_list_entry_get_next.side_effect = attrgetter('next')
        yield


EXPOSED_FUNCTIONS = [calls_to_libudev, libudev_list]


def pytest_namespace():
    return dict((f.__name__, f) for f in EXPOSED_FUNCTIONS)
