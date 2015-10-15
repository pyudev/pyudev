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

import abc
import os

from functools import reduce # pylint: disable=redefined-builtin

import six

from ._types import EdgeTypes
from ._types import NodeTypes

class HTMLUtils(object):
    """
    A class to handle HTML generation for HTML-style labels.
    """

    @staticmethod
    def make_table(rows):
        """
        Make an HTML table from a list of rows.

        :param rows: a list of rows as <td>...</td> strings
        :type rows: list of str
        :returns: HTML sring designating a table
        :rtype: str
        """
        table_attributes = "border=\"0\" cellborder=\"1\" cellspacing=\"0\""
        row_str = reduce(lambda x, y: x + y, rows, "")
        return "<table %s>%s</table>" % (table_attributes, row_str)

    @staticmethod
    def set_html_label(node, label):
        """
        Set an html label on a node.

        :param `Node` node: the node
        :param str label: the label
        """
        node.attr['label'] = "<%s>" % label
        node.attr['shape'] = 'none'


class Utils(object):
    """
    General utilities for graph transformations.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def copy_attr(attr):
        """
        Copy attr object to a dict of keys and values.

        :param attr: the attributes oject
        :returns: a dict of attributes
        :rtype: dict
        """
        return dict([(k, attr[k]) for k in attr])


@six.add_metaclass(abc.ABCMeta)
class GraphTransformer(object):
    """
    Abstract superclass of graph transformers.
    """

    @staticmethod
    @abc.abstractmethod
    def xform_object(graph, obj):
        """
        Transform ``obj``.

        :param `AGraph` graph: the graph
        :param obj: the object to transform
        """
        raise NotImplementedError()


    @classmethod
    @abc.abstractmethod
    def objects(cls, graph):
        """
        Locate the objects to transform.

        :param `AGraph` graph: the graph
        :returns: an iterable of objects
        :rtype: iterable
        """
        raise NotImplementedError()


    @classmethod
    def xform(cls, graph):
        """
        Do the transformation.

        :param `AGraph` graph: the graph
        """
        for obj in cls.objects(graph):
            cls.xform_object(graph, obj)


class PartitionTransformer(GraphTransformer):
    """
    Transforms nodes that are partitions.

    Sets node label to device name rather than device path.
    Sets node shape to triangle.
    """

    @staticmethod
    def xform_object(graph, obj):
        obj.attr['label'] = os.path.basename(obj.attr['DEVPATH'])
        obj.attr['shape'] = "triangle"

    @classmethod
    def objects(cls, graph):
        return (n for n in graph.iternodes() if \
           NodeTypes.is_type(n, NodeTypes.DEVICE_PATH) and \
           n.attr['DEVTYPE'] == 'partition')


class PartitionedDiskTransformer(GraphTransformer):
    """
    Transforms a partitioned disk into a partitioned node.

    Does not do anything if the disk has no partitions or if some
    non-partition edges point to any partitions.
    """

    @staticmethod
    def xform_object(graph, obj):
        partition_edges = [e for e in graph.out_edges(obj) if \
           EdgeTypes.is_type(e, EdgeTypes.PARTITION)]

        # If there are no partitions in this disk, do nothing
        if not partition_edges:
            return

        # partitions to include in label
        partitions = [e[1] for e in partition_edges]

        # edges to partitions that are not partition edges from node
        keep_edges = [e for e in graph.in_edges(partitions) \
           if not e in partition_edges]

        # Due to a a bug in pygraphviz, can not fix up edges to partitions.
        # If additional edges exist, skip.
        # See: https://github.com/pygraphviz/pygraphviz/issues/76
        if keep_edges:
            return

        # No edges besides partition edges, so build HTML label
        node_row = "<tr><td colspan=\"%s\">%s</td></tr>" % \
           (len(partitions) + 1, obj.attr['DEVPATH'])

        partition_names = sorted(
           os.path.basename(p.attr['DEVPATH']) for p in partitions
        )
        partition_data = reduce(
           lambda x, y: x + y,
           ("<td port=\"%s\">%s</td>" % (n, n) for n in partition_names),
           ""
        )
        partition_row = "<tr>%s</tr>" % (partition_data + "<td> </td>")
        table = HTMLUtils.make_table([node_row, partition_row])
        HTMLUtils.set_html_label(obj, table)

        # delete partition nodes, since they are accounted for in label
        graph.delete_nodes_from(partitions)

    @classmethod
    def objects(cls, graph):
        return (n for n in graph.iternodes() if \
           NodeTypes.is_type(n, NodeTypes.DEVICE_PATH) and \
           n.attr['DEVTYPE'] == 'disk')


class SpindleTransformer(GraphTransformer):
    """
    Make every actual physical spindle into a double octagon.
    """

    @staticmethod
    def xform_object(graph, obj):
        obj.attr['shape'] = "doubleoctagon"

    @classmethod
    def objects(cls, graph):
        return [n for n in graph.iternodes() if \
           NodeTypes.is_type(n, NodeTypes.WWN)]


class PartitionEdgeTransformer(GraphTransformer):
    """
    Make partition edges dashed.
    """

    @staticmethod
    def xform_object(graph, obj):
        obj.attr['style'] = 'dashed'

    @classmethod
    def objects(cls, graph):
        return (e for e in graph.iteredges() if \
           EdgeTypes.is_type(e, EdgeTypes.PARTITION))


class GraphTransformers(object):
    """
    A class that orders and does all graph transformations.
    """
    # pylint: disable=too-few-public-methods

    @classmethod
    def xform(cls, graph):
        """
        Transform a graph for more helpful viewing.

        :param `A_Graph` graph: the networkx graph
        """
        PartitionedDiskTransformer.xform(graph)
        SpindleTransformer.xform(graph)
        PartitionTransformer.xform(graph)
        PartitionEdgeTransformer.xform(graph)
