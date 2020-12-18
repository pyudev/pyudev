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
    utils.udev
    =====================

    Provide access the udev device database.

    Parses the udev device database from :program:`udevadm`.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

# isort: FUTURE
from __future__ import absolute_import, division, print_function, unicode_literals

# isort: STDLIB
import errno
import os
import re
import subprocess
import sys

# isort: THIRDPARTY
import six
from six.moves import collections_abc

six.add_move(
    six.MovedModule(
        "collections_abc",
        "collections",
        "collections.abc" if sys.version_info >= (3, 3) else "collections",
    )
)


class UDevAdm(object):
    """
    Wrap ``udevadm`` utility.
    """

    CANDIDATES = ["/sbin/udevadm", "udevadm"]
    _adm = None

    @classmethod
    def find(cls):
        """
        Construct a valid :class:`UDevAdm` object.

        :returns: a working :class:`UDevAdm` object
        :rtype: :class:`UDevAdm`
        :raises EnvironmentError:
        """
        for candidate in cls.CANDIDATES:
            try:
                udevadm = cls(candidate)
                # try to execute udev to make sure that it's actually
                # executable
                udevadm.query_udev_version()
                return udevadm
            except EnvironmentError as error:
                if error.errno != errno.ENOENT:
                    raise

    @classmethod
    def adm(cls):
        """
        Returns the singleton object of this class, if one can be found.

        :returns: singleton :class:`UDevAdm` object
        :rtype: :class:`UDevAdm`
        """
        if cls._adm is None:
            try:
                cls._adm = cls.find()
            except EnvironmentError:
                pass
        return cls._adm

    def __init__(self, udevadm):
        """
        Create a new ``udevadm`` wrapper for the given udevadm executable.

        ``udevadm`` is the path to udevadm as string.  If relative, ``udevadm``
        is looked up in ``$PATH``.
        """
        self.udevadm = udevadm

    def query_udev_version(self):
        """
        Return the version of udevadm.

        :returns: the udevadm version
        :rtype: int
        """
        return int(self._execute("--version"))

    def _execute(self, *args):
        """
        Execute a udevadm command.

        :raises CalledProcessError:
        """
        command = [self.udevadm] + list(args)
        proc = subprocess.Popen(command, stdout=subprocess.PIPE)
        output = proc.communicate()[0].strip()
        if proc.returncode != 0:
            raise subprocess.CalledProcessError(proc.returncode, command)
        return output

    def _execute_query(self, device_path, query_type="all"):
        """
        Execute a "udevadm info" query.

        :raises CalledProcessError:
        """
        output = self._execute(
            "info", "--root", "--path", device_path, "--query", query_type
        )
        return output.decode(sys.getfilesystemencoding())

    def query_devices(self):
        """
        Generate devices from udevadm database.

        Yields sys paths, minus the initial '/sys'.

        :raises CalledProcessError:
        """
        database = (
            self._execute("info", "--export-db")
            .decode(sys.getfilesystemencoding())
            .splitlines()
        )

        return (l[3:] for l in (l.strip() for l in database) if l[:3] == "P: ")

    def query_device_properties(self, device_path):
        """
        Return map of properties.

        :returns: a map of properties on the device
        :rtype: dict of str * str

        :raises CalledProcessError:
        """
        pairs = [
            l.strip().split("=", 1)
            for l in self._execute_query(device_path, "property").splitlines()
        ]

        if self.adm().query_udev_version() < 230:
            num_pairs = len(pairs)
            indices = [i for i in range(num_pairs) if pairs[i][1] == ""]
            pairs = [
                pairs[i]
                for i in range(num_pairs)
                if i not in indices and i - 1 not in indices
            ]

        return dict(pairs)

    def query_device_attributes(self, device_path):
        output = self._execute("info", "--attribute-walk", "--path", device_path)
        attribute_dump = output.decode(sys.getfilesystemencoding()).splitlines()
        attributes = {}
        for line in attribute_dump:
            line = line.strip()
            if line.startswith("looking at parent device"):
                # we don't continue with attributes of parent devices, we only
                # want the attributes of the given device
                break
            if line.startswith("ATTR"):
                name, value = line.split("==", 1)
                # remove quotation marks from attribute value
                value = value[1:-1]
                # remove prefix from attribute name
                name = re.search("{(.*)}", name).group(1)
                attributes[name] = value
        return attributes

    def query_device(self, device_path, query_type):
        if query_type not in ("symlink", "name"):
            raise ValueError(query_type)
        try:
            return self._execute_query(device_path, query_type)
        except subprocess.CalledProcessError:
            return None


class DeviceData(object):
    """
    Data for a single device.
    """

    def __init__(self, device_path, udevadm):
        self.device_path = device_path
        self._udevadm = udevadm

    def __repr__(self):
        return "{0}({1})".format(self.__class__.__name__, self.device_path)

    @property
    def sys_path(self):
        """
        Get the ``sysfs`` path of the device.
        """
        return "/sys" + self.device_path

    @property
    def exists(self):
        """
        Whether this device has some real existance on machine.

        :returns: True if the device does exist, otherwise False.
        :rtype: bool
        """
        return os.path.exists(self.sys_path)

    @property
    def properties(self):
        """
        Get the device properties as mapping of property names as strings to
        property values as strings.
        """
        return self._udevadm.query_device_properties(self.device_path)

    @property
    def attributes(self):
        """
        Get the device attributes as mapping of attributes names as strings to
        property values as byte strings.

        .. warning::

           As ``udevadm`` only exports printable attributes, this list can be
           incomplete!  Do *not* compare this dictionary directly to a
           attributes dictionary received through pyudev!
        """
        return self._udevadm.query_device_attributes(self.device_path)

    @property
    def tags(self):
        """
        Get the device tags as list of strings.
        """
        tags = self.properties.get("TAGS", "").split(":")
        return [t for t in tags if t]

    @property
    def device_node(self):
        """
        Get the device node path as string, or ``None`` if the device has no
        device node.
        """
        return self._udevadm.query_device(self.device_path, "name")

    @property
    def device_links(self):
        """
        Get the device links as list of strings.
        """
        links = self._udevadm.query_device(self.device_path, "symlink")
        return links.split() if links else []

    @property
    def device_number(self):
        """
        Get the device number as integer or 0 if the device has no device
        number.
        """
        device_node = self.device_node
        return 0 if device_node is None else os.stat(device_node).st_rdev


class DeviceDatabase(collections_abc.Iterable, collections_abc.Sized):
    """
    The udev device database.

    Takes a snapshot of the udev device database when it is initialized.
    Consequently, some :class:`DeviceData` objects in the database may
    not exist when the database is iterated over.

    This class is an iterable over :class:`DeviceData` objects that contain the
    data associated with each device stored in the udev database.
    """

    _db = None

    @classmethod
    def db(cls, renew=False):  # pylint: disable=invalid-name
        """
        Get a database object.

        :param bool renew: if renew is True, get a new object
        :returns: a database object
        :rtype: :class:`DeviceDatabase`
    """
        if cls._db is None or renew:
            udevadm = UDevAdm.adm()
            if udevadm:
                cls._db = DeviceDatabase(udevadm)
        return cls._db

    def __init__(self, udevadm):
        self._udevadm = udevadm
        self._devices = set(self._udevadm.query_devices())

    def __iter__(self):
        return (
            d for d in (DeviceData(d, self._udevadm) for d in self._devices) if d.exists
        )

    def __len__(self):
        return sum(1 for _ in self)

    def find_device_data(self, device_path):
        """
        Find device data for the device designated by ``device_path``.

        ``device_path`` is a string containing the device path.

        Return a :class:`DeviceData` object containing the data for the given
        device, or ``None`` if the device was not found.
        """
        data = DeviceData(device_path, self._udevadm)
        return data if data.exists and data in self else None
