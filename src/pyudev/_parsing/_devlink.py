# -*- coding: utf-8 -*-
# Copyright (C) 2015 Anne Mulhern <amulhern@redhat.com>

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
    pyudev.device._devlink
    ======================

    Simple Devlink class.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os


class Devlink(object):
    """
    Represents a device link.
    """

    def __init__(self, path):
        """
        Initializer

        :param str path: the full path of the device link
        """
        self._path = path

    def __str__(self):
        return self._path

    @property
    def path(self):
        """
        The full path of the device link.

        :returns: the full path
        :rtype: str
        """
        return self._path

    @property
    def has_category(self):
        """
        Whether this devlink has a category, like by-id, or by-path.

        :returns: True if the devlink has a category, otherwise False.
        :rtype: boolean

        This is decided by taking apart the path and looking for the lack
        of expected distinguishing features.
        """
        base = os.path.dirname(self._path)
        if not os.path.basename(base).startswith("by-"):
            return False

        return os.path.dirname(os.path.dirname(base)) == "/dev"

    @property
    def value(self):
        """
        The value of the devlink, which is the basename of the path.

        :returns: the basename, or None if this devlink has no category.
        :rtype: str or NoneType
        """
        if not self.has_category:
            return None
        return os.path.basename(self._path)

    @property
    def category(self):
        """
        The category of this device link.

        :returns: the category of the device link or None, if no category
        :rtype: str or NoneType
        """
        if not self.has_category:
            return None
        return os.path.basename(os.path.dirname(self._path))
