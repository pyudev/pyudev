# -*- coding: utf-8 -*-
# Copyright (c) 2010 Sebastian Wiesner <lunaryorn@googlemail.com>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from collections import defaultdict

from pyudev._libudev import libudev
from pyudev._core import Device


class DeviceTree(object):

    def __init__(self, enumerator):
        self._child_cache = defaultdict(set)
        self._build_tree(enumerator)

    def _build_tree(self, enumerator):
        for device in enumerator:
            self._child_cache[device.parent].add(device)
            for device in device.traverse():
                self._child_cache[device.parent].add(device)

    def __iter__(self):
        for device in self._child_cache[None]:
            yield DeviceTreeItem(self, device)

    def visit(self, visitor):
        for device in self:
            device.visit(visitor)

    def walk(self):
        for device in self:
            for item in device.walk():
                yield item


class DeviceTreeItem(Device):
    def __init__(self, tree, device):
        self.tree = tree
        # init this object by copying the device pointer
        Device.__init__(self, device.context,
                        libudev.udev_device_ref(device._device))

    @property
    def children(self):
        for child in self.tree._child_cache[self]:
            yield DeviceTreeItem(self.tree, child)

    def visit(self, visitor):
        visitor.visit(self)
        for child in self.children:
            child.visit(visitor)
        visitor.leave(self)

    def walk(self):
        children = list(self.children)
        yield self, children
        for child in children:
            for item in child.walk():
                yield item


class TreePrinter(object):
    def __init__(self):
        self.indent = 0

    def visit(self, device):
        print(' '*self.indent, device.device_path)
        self.indent += 2

    def leave(self, device):
        self.indent -= 2


def main():
    from pyudev import Context
    context = Context()
    tree = DeviceTree(context.list_devices())
    tree.visit(TreePrinter())


if __name__ == '__main__':
    main()

