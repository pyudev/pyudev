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
    pyudev_extras.graphs._types
    ===========================

    Types of graph nodes and edges.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

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
