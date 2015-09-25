# -*- coding: utf-8 -*-
# Copyright (C) 2015 Anne Mulhern <amulhern@redhat.com>

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
    tests.test_traversal
    ====================

    Tests traversing the sysfs hierarchy.

    .. moduleauthor:: mulhern <amulhern@redhat.com>
"""


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pyudev

import pytest

from hypothesis import given
from hypothesis import strategies
from hypothesis import Settings


_CONTEXT = pyudev.Context()
_DEVICES = _CONTEXT.list_devices()

# pylint: disable=too-many-function-args

SLAVES = [d for d in _DEVICES if list(pyudev.slaves(_CONTEXT, d, False))]

HOLDERS = [d for d in _DEVICES if list(pyudev.holders(_CONTEXT, d, False))]

BOTHS = list(set(SLAVES).intersection(set(HOLDERS)))

EITHERS = list(set(SLAVES).union(set(HOLDERS)))

NUM_TESTS = 5

# Use conditional to avoid processing tests if number of examples is too small.
# pytest.mark.skipif allows the test to be built, resulting in a hypothesis
# error if SLAVES or HOLDERS is empty.
if len(BOTHS) == 0:
    @pytest.mark.skipif(
       True,
       reason="no slaves or holders data for tests"
    )
    class TestTraversal(object):
        # pylint: disable=too-few-public-methods
        """
        An empty test class which is always skipped.
        """
        def test_dummy(self):
            """
            A dummy test, for which pytest can show a skip message.
            """
            pass
else:
    class TestTraversal(object):
        """
        A class for testing sysfs traversals.
        """
        @given(
           strategies.sampled_from(SLAVES),
           settings=Settings(max_examples=NUM_TESTS)
        )
        def test_slaves(self, device):
            """
            Verify slaves do not contain originating device.
            """
            assert device not in pyudev.slaves(_CONTEXT, device)

        @given(
           strategies.sampled_from(HOLDERS),
           settings=Settings(max_examples=NUM_TESTS)
        )
        def test_holders(self, device):
            """
            Verify holders do not contain originating device.
            """
            assert device not in pyudev.holders(_CONTEXT, device)

        @given(
           strategies.sampled_from(EITHERS),
           strategies.booleans(),
           settings=Settings(max_examples=2 * NUM_TESTS)
        )
        def test_inverse(self, device, recursive):
            """
            Verify that a round-trip traversal will encounter the original
            device.

            :param device: the device to test
            :param bool recursive: if True, test recursive relationship

            If recursive is True, test ancestor/descendant relationship.
            If recursive is False, tests parent/child relationship.
            """
            slaves = list(pyudev.slaves(_CONTEXT, device, recursive))
            for slave in slaves:
                assert device in list(
                   pyudev.holders(_CONTEXT, slave, recursive)
                )

            holders = list(pyudev.holders(_CONTEXT, device, recursive))
            for holder in holders:
                assert device in list(
                   pyudev.slaves(_CONTEXT, holder, recursive)
                )
