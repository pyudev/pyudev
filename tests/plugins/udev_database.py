# -*- coding: utf-8 -*-
# Copyright (C) 2012 Sebastian Wiesner <lunaryorn@gmail.com>

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
    plugins.udev_database
    =====================

    Provide access the udev device database.

    This plugin parses the udev device database from :program:`udevadm` and
    attaches it to the test configuration object.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@gmail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import pytest

from tests.utils import udev

def pytest_runtest_setup(item):
    """
    Evaluate the ``udev_version`` marker before running a test.
    """
    if not hasattr(item, 'obj'):
        return
    marker = getattr(item.obj, 'udev_version', None)
    if marker is not None:
        version_spec = marker.args[0]
        actual_version = item.config.udev_version
        if actual_version is None:
            pytest.skip('udev not found')
        elif not eval('{0} {1}'.format(actual_version, version_spec)):
            msg = 'udev version mismatch: {0} required, {1} found'.format(
                version_spec, actual_version)
            pytest.skip(msg)


def pytest_addoption(parser):
    group = parser.getgroup('udev_database', 'udev database configuration')
    group.addoption('--all-devices', action='store_true',
                    help='Run device tests against *all* devices in the '
                    'database.  By default, only a random sample will be '
                    'checked.', default=False)
    group.addoption('--device', metavar='DEVICE',
                    help='Run the device tests only against the given '
                    'DEVICE', default=None)
    group.addoption('--device-sample-size', type='int', metavar='N',
                    help='Use a random sample of N elements (default: 10)',
                    default=10)


def pytest_configure(config):
    # register a marker for required udev versions
    config.addinivalue_line(
        'markers', 'udev_version(spec): mark test to run only if the udev '
        'version matches the given version spec')

    udevadm = udev.UDevAdm.adm()
    if udevadm:
        config.udev_version = udevadm.query_udev_version()
        config.udev_database = udev.DeviceDatabase.db()

        if config.option.all_devices:
            sample_size = None
        else:
            sample_size = config.option.device_sample_size

        config.udev_device_sample = udev.get_device_sample(
           config.udev_database,
           config.option.device,
           sample_size
        )
    else:
        config.udev_version = None
        config.udev_database = None
        config.udev_device_sample = []
