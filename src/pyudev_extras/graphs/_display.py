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
    pyudev_extras.graphs._display
    =============================

    Tools to display graphs of various kinds.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

import networkx as nx

from ._types import EdgeTypes
from ._types import NodeTypes


class GraphTransformers(object):
    """
    A collection of graph transformers.
    """

    @staticmethod
    def copy_attr(attr):
        """
        Copy attr object to a dict of keys and values.

        :param attr: the attributes oject
        :returns: a dict of attributes
        :rtype: dict
        """
        return dict([(k, attr[k]) for k in attr])

    @staticmethod
    def xform_partition(node):
        """
        Transform a partition device so that its label is just the device name.
        """
        node.attr['label'] = os.path.basename(node.attr['DEVPATH'])


    @classmethod
    def xform_partitioned(cls, graph, node):
        """
        Place a disk node w/edges to partitions in a subgraph
        that contains it and the partitions.

        :param `AGraph` graph: the graph
        :param `Node` node: the node

        :returns: the new cluster formed
        :rtype: `AGraph`
        """
        # Find partitions of node
        partition_edges = [e for e in graph.out_edges(node) if \
           EdgeTypes.is_type(e, EdgeTypes.PARTITION)]
        partitions = [e[1] for e in partition_edges]

        cluster = graph.add_subgraph(
           partitions + [node],
           name='cluster' + node.name,
        )

        node.attr['shape'] = "plaintext"
        for edge in partition_edges:
            edge.attr['color'] = 'white'

        return cluster

    @classmethod
    def xform_partitions(cls, graph):
        """
        Transformations on partitions and their parents.

        :param `AGraph` graph: the graph
        """
        partition_edges = [e for e in graph.iteredges() if \
               EdgeTypes.is_type(e, EdgeTypes.PARTITION)]

        while partition_edges:
            cluster = cls.xform_partitioned(graph, partition_edges[0][0])
            partition_edges = [e for e in partition_edges \
               if e not in cluster.edges()]

        partitions = (n for n in graph.iternodes() if \
           NodeTypes.is_type(n, NodeTypes.DEVICE_PATH) and \
           n.attr['DEVTYPE'] == 'partition')

        for partition in partitions:
            cls.xform_partition(partition)

    @classmethod
    def xform(cls, graph):
        """
        Transform a networkx multigraph to a graphviz graph.

        :param `DiMultiGraph` graph: the networkx graph
        :returns: the new graph
        :rtype: `A_Graph`
        """
        res = nx.to_agraph(graph)
        cls.xform_partitions(graph)
        return res
