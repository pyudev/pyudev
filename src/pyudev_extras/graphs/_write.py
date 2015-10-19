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
    pyudev_extras.graphs._write
    ===========================

    Tools to write out a graph.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import networkx as nx


class Rewriter(object):
    """
    Rewrite graph for output.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def stringize(graph):
        """
        Xform node and edge types to strings.
        """
        edge_types = nx.get_edge_attributes(graph, 'edgetype')
        for key, value in edge_types.items():
            edge_types[key] = str(value)
        nx.set_edge_attributes(graph, 'edgetype', edge_types)

        node_types = nx.get_node_attributes(graph, 'nodetype')
        for key, value in node_types.items():
            node_types[key] = str(value)
        nx.set_node_attributes(graph, 'nodetype', node_types)
