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
    pyudev.traversal
    ================

    Traversing the sysfs hierarchy.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import functools
import os

from pyudev.device import Device

__all__ = ['topology_walk', 'slaves', 'holders']

def topology_walk(top, follow_slaves=True, recursive=True):
    """
        Walk the sysfs directory in depth first search,
        yielding directories corresponding to devices in sysfs.

        :param str top: directory to begin at
        :param bool follow_slaves: if True, follow slaves, otherwise, holders
        :param bool recursive: if False, only show one level

        ``top`` itself is not in the result.
    """
    link_dir = os.path.join(top, 'slaves' if follow_slaves else 'holders')

    if os.path.isdir(link_dir):
        names = os.listdir(link_dir)
        files = (os.path.abspath(os.path.join(link_dir, f)) for f in names)
        links = (os.readlink(f) for f in files if os.path.islink(f))
        devs = (os.path.normpath(os.path.join(link_dir, l)) for l in links)
        for dev in devs:
            if recursive:
                for res in topology_walk(dev, follow_slaves):
                    yield res
            yield dev

def device_wrapper(func):
    """ Wraps function so that it returns Device rather than directory. """

    @functools.wraps(func)
    def new_func(context, device, recursive=True):
        """
        New function wraps yielded value in Device.

        :param :class:`Context` context: udev context
        :param :class:`Device` device: device to start from
        :param bool recursive: if False, only show immediate slaves
        """
        for directory in func(device.sys_path, recursive):
            yield Device.from_sys_path(context, directory)

    return new_func

@device_wrapper
def slaves(device, recursive=True):
    """
    Yield slaves of ``device``.

    :param :class:`Context` context: udev context
    :param class:`Device` device: device to start from
    :param bool recursive: if False, only show immediate slaves
    """
    return topology_walk(device, True, recursive)

@device_wrapper
def holders(device, recursive=True):
    """
    Yield holders of ``device``.

    :param :class:`Context` context: udev context
    :param :class:`Device` device: device to start from
    :param bool recursive: if False, only show immediate holders
    """
    return topology_walk(device, False, recursive)
