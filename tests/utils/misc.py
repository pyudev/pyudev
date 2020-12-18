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
    utils.misc
    =============

    Miscellaneous useful methods.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

# isort: FUTURE
from __future__ import absolute_import, division, print_function, unicode_literals

# isort: STDLIB
from functools import wraps

# isort: THIRDPARTY
import pytest
import six
from hypothesis.core import FailedHealthCheck


def is_unicode_string(value):
    """
    Return ``True``, if ``value`` is of a real unicode string type
    (``unicode`` in python 2, ``str`` in python 3), ``False`` otherwise.
    """
    return isinstance(value, unicode if six.PY2 else str)


def failed_health_check_wrapper(func):
    """
    If the test fails a health check, calls skip().
    """

    @wraps(func)
    def the_func(*args):
        """
        Catch a hypothesis FailedHealthCheck exception and log it as a skip.
        """
        try:
            func(*args)
        except FailedHealthCheck:
            func_code = six.get_function_code(func)
            pytest.skip(
                "failed health check for %s() (%s: %s)"
                % (func_code.co_name, func_code.co_filename, func_code.co_firstlineno)
            )

    return the_func
