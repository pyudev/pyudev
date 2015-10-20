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
    pyudev_extras.graphs._utils
    ===========================

    Generic utilities.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import networkx as nx


class GraphUtils(object):
    """
    Generic utilties for graphs.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def get_roots(graph):
        """
        Get the roots of a graph.

        :param `MultiDiGraph` graph: the graph

        :returns: the roots (or leaves) of the graph
        :rtype: list of `Node`
        """
        return [n for n in nx.nodes_iter(graph) if not nx.ancestors(graph, n)]
