# -*- coding: utf-8 -*-
# Copyright (c) 2011 Sebastian Wiesner <lunaryorn@googlemail.com>

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

"""
    pyudev._compat
    ==============

    Compatibility for Python versions, that lack certain functions.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""


from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from subprocess import Popen, CalledProcessError, PIPE


def check_output(command):
    """
    Compatibility with :func:`subprocess.check_output` from Python 2.7 and
    upwards.
    """
    proc = Popen(command, stdout=PIPE)
    output = proc.communicate()[0]
    if proc.returncode != 0:
        raise CalledProcessError(proc.returncode, command)
    return output
