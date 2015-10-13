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
        node.attr['shape'] = "triangle"


    @classmethod
    def xform_partitions(cls, graph):
        """
        Transformations on partitions.

        :param `AGraph` graph: the graph
        """
        partitions = (n for n in graph.iternodes() if \
           NodeTypes.is_type(n, NodeTypes.DEVICE_PATH) and \
           n.attr['DEVTYPE'] == 'partition')

        for partition in partitions:
            cls.xform_partition(partition)

    @classmethod
    def xform_disk(cls, graph, node):
        """
        Make a cluster of a disk and its partitions.

        :param `AGraph` graph: the graph
        :param `Node` node: the node

        If the disk is not partitioned, no cluster is made.

        """

        partition_edges = [e for e in graph.out_edges(node) if \
           EdgeTypes.is_type(e, EdgeTypes.PARTITION)]

        if partition_edges:
            partitions = [e[1] for e in partition_edges]
            graph.add_subgraph(
               partitions + [node],
               name='cluster' + node.name,
            )

            node.attr['shape'] = "plaintext"
            for edge in partition_edges:
                edge.attr['color'] = 'white'

    @classmethod
    def xform_disks(cls, graph):
        """
        Transformations on disks.

        :param `AGraph` graph: the graph
        """
        disks = [n for n in graph.iternodes() if \
           NodeTypes.is_type(n, NodeTypes.DEVICE_PATH) and \
           n.attr['DEVTYPE'] == 'disk']

        for disk in disks:
            cls.xform_disk(graph, disk)

    @staticmethod
    def xform_spindle(node):
        """
        Transform a spindle so that it is visually arresting.

        :param `Node` node: the node
        """
        node.attr['shape'] = "doubleoctagon"

    @classmethod
    def xform_spindles(cls, graph):
        """
        Transformation on spindles.

        :param `AGraph` graph: the graph
        """
        spindles = [n for n in graph.iternodes() if \
           NodeTypes.is_type(n, NodeTypes.WWN)]

        for spindle in spindles:
            cls.xform_spindle(spindle)

    @classmethod
    def xform(cls, graph):
        """
        Transform a graph for more helpful viewing.

        :param `A_Graph` graph: the networkx graph
        """
        cls.xform_partitions(graph)
        cls.xform_disks(graph)
