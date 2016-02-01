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
    tests.test_parsing
    ==================

    Test parsing values that happen to be synthesized from other values
    such that they need to be parsed.

    .. moduleauthor:: mulhern <amulhern@redhat.com>
"""


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pyudev

import pytest

from hypothesis import given
from hypothesis import strategies

_CONTEXT = pyudev.Context()
_DEVICES = _CONTEXT.list_devices()


class TestIDPATH(object):
    """
    Test parsing ID_PATH values.
    """

    @given(
       strategies.sampled_from(_DEVICES).filter(
          lambda x: x.get('ID_PATH') is not None
       )
    )
    def test_parsing(self, a_device):
        """
        Test that parsing is satisfactory on all examples.
        """
        id_path = a_device.get('ID_PATH')
        parser = pyudev.IdPathParse(pyudev.IdPathParsers.PARSERS)
        result = parser.parse(id_path)
        assert isinstance(result, list) and result != []

    _devices = [d for d in _DEVICES if d.get('ID_SAS_PATH') is not None]
    if len(_devices) > 0:
        @given(strategies.sampled_from(_devices))
        def test_parsing_sas_path(self, a_device):
            """
            Test that parsing is satisfactory on all examples.
            """
            id_path = a_device.get('ID_SAS_PATH')
            parser = pyudev.IdPathParse(pyudev.IdPathParsers.PARSERS)
            result = parser.parse(id_path)
            assert isinstance(result, list) and result != []
    else:
        def test_parsing_sas_path(self):
            # pylint: disable=missing-docstring
            pytest.skip("not enough devices w/ ID_SAS_PATH property")
