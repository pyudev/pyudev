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
    pyudev_extras.graphs._decorations
    =================================

    Tools to decorate networkx graphs in situ, i.e., as
    constructed rather than as read from a textual file.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import networkx as nx

import pyudev

from ._types import NodeTypes


class UdevProperties(object):
    """
    Find udev properties for the device nodes of a network graph.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def decorated(graph):
        """
        Returns elements that get decorated.
        """
        node_types = nx.get_node_attributes(graph, 'nodetype')
        return (k for k in node_types \
           if node_types[k] is NodeTypes.DEVICE_PATH)

    @staticmethod
    def properties(context, element, names):
        """
        Get properties on this element.
        """
        device = pyudev.Devices.from_path(context, element)
        return dict((k, device[k]) for k in names if k in device)

    @classmethod
    def udev_properties(cls, context, graph, names):
        """
        Get udev properties for graph nodes that correspond to devices.

        :param `Context` context: the udev context
        :param graph: the graph
        :param names: a list of property keys
        :type names: list of str

        :returns: dict of property name, node, property value
        :rtype: dict
        """
        dicts = {'UDEV' : dict()}
        for node in cls.decorated(graph):
            dicts['UDEV'][node] = cls.properties(context, node, names)

        return dicts


class Decorator(object):
    """
    Decorate graph elements with attributes.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def decorate(graph, properties):
        """
        Decorate the graph.

        :param `MultiDiGraph` graph: the graph
        :param properties: a dict of properties
        :type properties: dict of property name -> graph element -> value
        """

        for property_name, value in properties.items():
            nx.set_node_attributes(graph, property_name, value)
