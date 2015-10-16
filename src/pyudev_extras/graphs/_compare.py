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
    pyudev_extras.graphs._compare
    =============================

    Compare graphs to determine if they represent the same storage
    configuration.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import networkx.algorithms.isomorphism as iso


def _node_match(attr1, attr2):
    """
    Returns True if nodes with the given attrs should be considered
    equivalent.

    :param dict attr1: attributes of first node
    :param dict attr2: attributes of second node

    :return: True if nodes are equivalent, otherwise False
    :rtype: bool
    """
    type1 = attr1['nodetype']
    type2 = attr2['nodetype']

    if type1 != type2:
        return False

    return attr1['identifier'] == attr2['identifier']


class Compare(object):
    """
    Compare two storage graphs.
    """
    # pylint: disable=too-few-public-methods

    @classmethod
    def is_equivalent(cls, graph1, graph2):
        """
        Whether these graphs represent equivalent storage configurations.

        :param graph1: a graph
        :param graph2: a graph

        :returns: True if the graphs are equivalent, otherwise False
        :rtype: bool
        """
        return iso.is_isomorphic(
           graph1,
           graph2,
           _node_match,
           iso.categorical_edge_match('edgetype', None)
        )
