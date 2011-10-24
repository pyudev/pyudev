# -*- coding: utf-8 -*-
# Copyright (C) 2011 Sebastian Wiesner <lunaryorn@googlemail.com>

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
    pyudev._py3util
    ===============

    Internal utilities for Python 3.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""


def reraise(exc, traceback):
    """
    Re-raise the given exception with ``traceback``.

    ``exc`` is an exception derived from :class:`~exceptions.Exception`,
    ``traceback`` a traceback object.
    """
    raise exc.with_traceback(traceback)
