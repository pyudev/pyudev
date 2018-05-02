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
    plugins.privileged
    ==================

    Support privileged operations to trigger real udev events.

    This plugin adds :func:`load_dummy` and :func:`unload_dummy` to the
    :mod:`pytest` namespace.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@gmail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from subprocess import call

import pytest


def pytest_addoption(parser):
    group = parser.getgroup('privileged', 'tests with privileged operations')
    group.addoption(
        '--enable-privileged',
        action='store_true',
        help='Enable tests that required privileged operations',
        default=False)


def check_privileges_or_skip():
    if not pytest.config.option.enable_privileged:
        pytest.skip('privileged tests disabled')


def load_dummy():
    """
    Load the ``dummy`` module.

    If privileged tests are disabled, the current test is skipped.
    """
    check_privileges_or_skip()
    call(['sudo', 'modprobe', 'dummy'])


def unload_dummy():
    """
    Unload the ``dummy`` module.

    If privileged tests are disabled, the current test is skipped.
    """
    check_privileges_or_skip()
    call(['sudo', 'modprobe', '-r', 'dummy'])


EXPOSED_FUNCTIONS = [load_dummy, unload_dummy]


def pytest_namespace():
    return dict((f.__name__, f) for f in EXPOSED_FUNCTIONS)
