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
    tests.test_graphs
    =================

    Tests graph generation.

    .. moduleauthor:: mulhern <amulhern@redhat.com>
"""


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

import networkx as nx

import pyudev

from pyudev_extras import graphs
from pyudev_extras import traversal

import pytest

from hypothesis import given
from hypothesis import strategies
from hypothesis import Settings


_CONTEXT = pyudev.Context()
_DEVICES = _CONTEXT.list_devices()

# pylint: disable=too-many-function-args

SLAVES = [d for d in _DEVICES if list(traversal.slaves(_CONTEXT, d, False))]

HOLDERS = [d for d in _DEVICES if list(traversal.holders(_CONTEXT, d, False))]

EITHERS = list(set(SLAVES).union(set(HOLDERS)))

NUM_TESTS = 5

# Use conditional to avoid processing tests if number of examples is too small.
# pytest.mark.skipif allows the test to be built, resulting in a hypothesis
# error if SLAVES or HOLDERS is empty.
if len(EITHERS) == 0:
    @pytest.mark.skipif(
       True,
       reason="no slaves or holders data for tests"
    )
    class TestSysfsTraversal(object):
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
    class TestSysfsTraversal(object):
        """
        A class for testing graphs generated entirely from sysfs traversals.
        """
        @given(
           strategies.sampled_from(EITHERS),
           settings=Settings(max_examples=NUM_TESTS)
        )
        def test_slaves(self, device):
            """
            Verify slaves graph has same number of nodes as traversal.

            Traversal may contain duplicates, while graph should eliminate
            duplicates during its construction. Traversal results does not
            include origin device, graph nodes do.
            """
            slaves = list(traversal.slaves(_CONTEXT, device))
            graph = graphs.SysfsTraversal.slaves(_CONTEXT, device)
            graph_len = len(graph)
            assert len(set(slaves)) == (graph_len - 1 if graph_len else 0)

        @given(
           strategies.sampled_from(EITHERS),
           settings=Settings(max_examples=NUM_TESTS)
        )
        def test_holders(self, device):
            """
            Verify holders graph has same number of nodes as traversal.

            Traversal may contain duplicates, while graph should eliminate
            duplicates during its construction. Traversal results does not
            include origin device, graph nodes do.
            """
            holders = list(traversal.holders(_CONTEXT, device))
            graph = graphs.SysfsTraversal.holders(_CONTEXT, device)
            graph_len = len(graph)
            assert len(set(holders)) == (graph_len - 1 if graph_len else 0)

class TestSysfsGraphs(object):
    """
    Test building various graphs.
    """

    def test_complete(self):
        """
        There is an equivalence between the nodes in the graph
        and the devices graphed.

        Moreover, all nodes have node_type DEVICE_PATH and all edges have
        type SLAVE.
        """
        graph = graphs.SysfsGraphs.complete(_CONTEXT, subsystem="block")
        devs = list(_CONTEXT.list_devices(subsystem="block"))
        assert nx.number_of_nodes(graph) == len(set(devs))
        assert set(nx.nodes(graph)) == set(d.device_path for d in devs)

        types = nx.get_node_attributes(graph, "node_type")
        assert all(t is graphs.NodeTypes.DEVICE_PATH for t in types.values())

        types = nx.get_edge_attributes(graph, "edge_type")
        assert all(t is graphs.EdgeTypes.SLAVE for t in types.values())
