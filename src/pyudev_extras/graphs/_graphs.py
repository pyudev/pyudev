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
    pyudev_extras.graphs
    ====================

    Tools to build graphs of various kinds.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import networkx as nx

from ._decorations import Decorator
from ._decorations import UdevProperties

from . import _display
from . import _print
from . import _structure
from . import _utils
from . import _write


class GenerateGraph(object):
    """
    Coordinate graph generating activities.
    """

    @staticmethod
    def get_graph(context, name):
        """
        Get a complete graph storage graph.

        :param `Context` context: the libudev context
        :return: the generated graph
        :rtype: `MultiDiGraph`
        """
        graph_classes = [
           _structure.DMPartitionGraphs,
           _structure.PartitionGraphs,
           _structure.SpindleGraphs,
           _structure.SysfsBlockGraphs
        ]
        return nx.compose_all(
           (t.complete(context) for t in graph_classes),
           name=name
        )

    @staticmethod
    def decorate_graph(context, graph):
        """
        Decorate a graph with additional properties.

        :param `Context` context: the libudev context
        :param `MultiDiGraph` graph: the graph
        """
        properties = ['DEVNAME', 'DEVPATH', 'DEVTYPE']
        table = UdevProperties.udev_properties(context, graph, properties)
        Decorator.decorate(graph, table)


class RewriteGraph(object):
    """
    Convert graph so that it is writable.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def convert_graph(graph):
        """
        Do any necessary graph conversions so that it can be output.

        """
        _write.Rewriter.stringize(graph)


class DisplayGraph(object):
    """
    Displaying a generated multigraph by transformation to a graphviz graph.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def convert_graph(graph):
        """
        Convert graph to graphviz format.

        :param `MultiDiGraph` graph: the graph
        :returns: a graphviz graph

        Designate its general layout and mark or rearrange nodes as appropriate.
        """
        dot_graph = nx.to_agraph(graph)
        dot_graph.graph_attr.update(rankdir="LR")
        dot_graph.layout(prog="dot")

        xformers = [
           _display.PartitionedDiskTransformer,
           _display.SpindleTransformer,
           _display.PartitionTransformer,
           _display.PartitionEdgeTransformer,
           _display.CongruenceEdgeTransformer
        ]

        _display.GraphTransformers.xform(dot_graph, xformers)
        return dot_graph


class PrintGraph(object):
    """
    Print a textual representation of the graph.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def print_graph(out, graph, inverse=False):
        """
        Print a graph.

        :param `file` out: print destination
        :param `MultiDiGraph` graph: the graph
        """
        if inverse:
            graph = graph.reverse(copy=True)

        key_map = nx.get_node_attributes(graph, 'identifier')
        key_func = lambda n: key_map[n]
        roots = sorted(_utils.GraphUtils.get_roots(graph), key=key_func)

        udev_map = nx.get_node_attributes(graph, 'UDEV')

        def info_func(node):
            """
            Function to generate information to be printed for ``node``.

            :param `Node` node: the node
            :returns: a list of informational strings
            :rtype: list of str
            """
            udev_info = udev_map.get(node)
            devname = udev_info and udev_info.get('DEVNAME')
            return [devname or key_map[node]]

        for root in roots:
            _print.Print.output_nodes(
               out,
               info_func,
               '{0}',
               graph,
               True,
               0,
               root
            )
