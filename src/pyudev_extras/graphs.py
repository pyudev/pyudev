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

from collections import namedtuple

import networkx as nx

from . import traversal

class NodeType(object):
    """
    Abstract class that represents a node type.
    """
    # pylint: disable=too-few-public-methods

    def __str__(self): # pragma: no cover
        return self.__class__.__name__
    __repr__ = __str__

class DevicePath(NodeType):
    """
    A device, uniquely identified by its device path.
    """
    # pylint: disable=too-few-public-methods
    pass

DevicePath = DevicePath() # pylint: disable=invalid-name

class NodeTypes(object):
    """
    Enumeration of node types.
    """
    # pylint: disable=too-few-public-methods
    DEVICE_PATH = DevicePath

    @staticmethod
    def is_type(node, node_type):
        """
        Whether ``node`` has type ``node_type``.

        :param `agraph.Edge` node: the node
        :param `EdgeType` node_type: an node type
        :returns: True if ``node`` has type ``node_type``, otherwise False
        :rtype: bool
        """
        return node.attr['node_type'] == str(node_type)

class EdgeType(object):
    """
    Superclass of edge types.
    """
    # pylint: disable=too-few-public-methods

    def __str__(self): # pragma: no cover
        return self.__class__.__name__
    __repr__ = __str__

class Slave(EdgeType):
    """
    Encodes slaves/holders relationship.
    """
    # pylint: disable=too-few-public-methods
    pass

Slave = Slave() # pylint: disable=invalid-name

class Partition(EdgeType):
    """
    Encodes partition relationship.
    """
    # pylint: disable=too-few-public-methods
    pass

Partition = Partition() # pylint: disable=invalid-name

class EdgeTypes(object):
    """
    Enumeration of edge types.
    """
    # pylint: disable=too-few-public-methods
    SLAVE = Slave
    PARTITION = Partition

    @staticmethod
    def is_type(edge, edge_type):
        """
        Whether ``edge`` has type ``edge_type``.

        :param `agraph.Edge` edge: the edge
        :param `EdgeType` edge_type: an edge type
        :returns: True if ``edge`` has type ``edge_type``, otherwise False
        :rtype: bool
        """
        return edge.attr['edge_type'] == str(edge_type)

SysfsTraversalConfig = namedtuple(
   'SysfsTraversalConfig',
   ['recursive', 'slaves']
)


class GraphMethods(object):
    """
    Generic graph methods.
    """

    @staticmethod
    def add_nodes(graph, nodes, node_type):
        """
        Add nodes in ``nodes`` to graph.

        :param `MultiDiGraph` graph: the graph
        :param nodes: source nodes
        :type nodes: list of object
        :param `NodeType` node_type: a node type

        Nodes are device_paths of each device, as these uniquely identify
        the device.
        """
        graph.add_nodes_from(nodes, node_type=node_type)


    @staticmethod
    def add_edges(graph, sources, targets, edge_type, node_type):
        """
        Add edges to graph from sources to targets.

        :param `MultiDiGraph` graph: the graph
        :param sources: source nodes
        :type sources: list of `object`
        :param targets: target nodes
        :type targets: list of `object`
        :param `EdgeType` edge_type: type for edges
        :param `NodeType` node_type: type for nodes

        Nodes are device_paths of each device, as these uniquely identify
        the device.
        """
        graph.add_nodes_from(sources + targets, node_type=node_type)
        edges = ((x, y) for x in sources for y in targets)
        graph.add_edges_from(edges, edge_type=edge_type)


class SysfsTraversal(object):
    """
    Build simple graph from the holders or slaves of a given device.
    """

    @classmethod
    def do_level(cls, graph, context, device, config):
        """
        Recursively defined function to generate a graph from ``device``.

        :param `MultiDiGraph` graph: the graph
        :param `Context` context: the libudev context
        :param `Device` device: the device
        :param `SysfsTraversalConfig` config: traversal configuration
        """
        func = traversal.slaves if config.slaves else traversal.holders
        level = list(func(context, device, False))

        if config.slaves:
            sources = [device]
            targets = level
        else:
            sources = level
            targets = [device]

        if not level:
            GraphMethods.add_nodes(
               graph,
               [device.device_path],
               NodeTypes.DEVICE_PATH
            )
            return

        GraphMethods.add_edges(
           graph,
           [dev.device_path for dev in sources],
           [dev.device_path for dev in targets],
           EdgeTypes.SLAVE,
           NodeTypes.DEVICE_PATH
        )

        if config.recursive:
            for dev in level:
                cls.do_level(graph, context, dev, config)

    @classmethod
    def sysfs_traversal(cls, context, device, config):
        """
        General graph of a sysfs traversal.

        :param `Context` context: the libudev context
        :param `Device` device: the device
        :param `SysfsTraversalConfig` config: traversal configuration
        :returns: a graph
        :rtype: `MultiDiGraph`
        """
        graph = nx.MultiDiGraph()
        cls.do_level(graph, context, device, config)
        return graph

    @classmethod
    def holders(cls, context, device, recursive=True):
        """
        Yield graph of slaves of device, including the device.

        :param `Context` context: the libudev context
        :param `Device` device: the device
        :param bool recursive: True for recursive, False otherwise
        :returns: a graph
        :rtype: `MultiDiGraph`
        """
        config = SysfsTraversalConfig(slaves=False, recursive=recursive)
        return cls.sysfs_traversal(context, device, config)

    @classmethod
    def slaves(cls, context, device, recursive=True):
        """
        Yield graph of slaves of device, including the device.

        :param `Context` context: the libudev context
        :param `Device` device: the device
        :param bool recursive: True for recursive, False otherwise
        :returns: a graph
        :rtype: `MultiDiGraph`
        """
        config = SysfsTraversalConfig(slaves=True, recursive=recursive)
        return cls.sysfs_traversal(context, device, config)


class SysfsGraphs(object):
    """
    Build sysfs graphs in various ways.
    """

    @staticmethod
    def slaves_and_holders(context, device, recursive=True):
        """
        Make a graph of slaves and holders of a device.

        :param `Context` context: the libudev context
        :param `Device` device: the device
        :param bool recursive: True for recursive, False otherwise
        :returns: a graph
        :rtype: `MultiDiGraph`
        """
        return nx.compose(
           SysfsTraversal.slaves(context, device, recursive),
           SysfsTraversal.holders(context, device, recursive)
        )

    @classmethod
    def parents_and_children(cls, context, device):
        """
        Make a graph of the parents and children of a device.

        :param `Context` context: the libudev context
        :param `Device` device: the device
        :returns: a graph
        :rtype: `MultiDiGraph`
        """
        return cls.slaves_and_holders(context, device, recursive=False)

    @classmethod
    def complete(cls, context, **kwargs):
        """
        Build a complete graph showing all devices.

        :param `Context` context: a udev context
        :param kwargs: arguments for filtering the devices.
        :returns: a graph
        :rtype: `MultiDiGraph`
        """
        # pylint: disable=star-args
        devices = (d for d in context.list_devices(**kwargs))
        graphs = (cls.parents_and_children(context, d) for d in devices)
        return reduce(nx.compose, graphs, nx.MultiDiGraph())


class PartitionGraphs(object):
    """
    Build graphs of partition relationships.
    """

    @staticmethod
    def partition_graph(device):
        """
        Make a graph of partition relationships.

        :param `Device` device: the partition device
        :returns: a graph
        :rtype: `MultiDiGraph`
        """
        graph = nx.MultiDiGraph()
        parent = device.parent
        GraphMethods.add_edges(
           graph,
           [parent.device_path],
           [device.device_path],
           EdgeTypes.PARTITION,
           NodeTypes.DEVICE_PATH
        )
        return graph

    @classmethod
    def complete(cls, context):
        """
        Build a complete graph of all partitions.

        :param `Context` context: a udev context
        :returns: a graph
        :rtype: `MultiDiGraph`
        """
        block_devices = context.list_devices(subsystem="block")
        partitions = block_devices.match_property('DEVTYPE', 'partition')
        graphs = (cls.partition_graph(d) for d in partitions)
        return reduce(nx.compose, graphs, nx.MultiDiGraph())


class DisplayGraph(object):
    """
    Ways to display a graph.
    """

    # pylint: disable=too-few-public-methods

    @classmethod
    def to_dot(cls, graph, out):
        """
        Dot file from graph.

        :param `MultiDiGraph` graph: the graph
        :param file out: output file to write graph to
        """
        dot_graph = nx.to_agraph(graph)
        dot_graph.layout(prog="dot")
        print(dot_graph.string(), file=out)
