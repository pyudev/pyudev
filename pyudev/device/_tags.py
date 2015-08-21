# -*- coding: utf-8 -*-
# Copyright (C) 2011, 2012 Sebastian Wiesner <lunaryorn@gmail.com>

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
    pyudev.device._tags
    =====================

    Tags associated with a Device.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@gmail.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import Container, Iterable

from pyudev._util import ensure_byte_string
from pyudev._util import ensure_unicode_string
from pyudev._util import udev_list_iterate

class Tags(Iterable, Container):
    """
    A iterable over :class:`Device` tags.

    Subclasses the ``Container`` and the ``Iterable`` ABC.
    """

    # pylint: disable=too-few-public-methods

    def __init__(self, device):
        self.device = device

    def _has_tag(self, tag):
        """
            Whether ``tag`` exists.

            :param tag: unicode string with name of tag
            :rtype: bool
        """
        if hasattr(self._libudev, 'udev_device_has_tag'):
            return bool(self._libudev.udev_device_has_tag(
                self.device, ensure_byte_string(tag)))
        else:
            return any(t == tag for t in self)

    @property
    def _libudev(self):
        return self.device._libudev

    def __contains__(self, tag):
        """
        Check for existence of ``tag``.

        ``tag`` is a tag as unicode string.

        Return ``True``, if ``tag`` is attached to the device, ``False``
        otherwise.
        """
        return self._has_tag(tag)

    def __iter__(self):
        """
        Iterate over all tags.

        Yield each tag as unicode string.
        """
        tags = self._libudev.udev_device_get_tags_list_entry(self.device)
        for tag, _ in udev_list_iterate(self._libudev, tags):
            yield ensure_unicode_string(tag)
