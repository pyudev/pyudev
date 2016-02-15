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

from itertools import groupby

import pyudev

from pyudev import _parsing

import pytest

from hypothesis import given
from hypothesis import settings
from hypothesis import strategies

_CONTEXT = pyudev.Context()
_DEVICES = _CONTEXT.list_devices()


class TestIDPATH(object):
    """
    Test parsing ID_PATH values.
    """
    # pylint: disable=too-few-public-methods
    _devices = [d for d in _DEVICES if d.get('ID_PATH') is not None]
    @pytest.mark.skipif(
       len(_devices) == 0,
       reason="no devices with ID_PATH property"
    )
    @given(strategies.sampled_from(_devices))
    @settings(min_satisfying_examples=1)
    def test_parsing(self, a_device):
        """
        Test that parsing is satisfactory on all examples.
        """
        parsers = _parsing.IdPathParsers.PARSERS
        id_path = a_device.get('ID_PATH')
        parser = _parsing.IdPathParse(parsers)
        result = parser.parse(id_path)
        assert isinstance(result, list) and result != []
        assert all(
           any(r[1].group('total').startswith(p.prefix) for p in parsers) \
                   for r in result
        )
        assert not any(r[1].group('total').startswith('-') for r in result)

    _devices = [d for d in _DEVICES if d.get('ID_SAS_PATH') is not None]
    @pytest.mark.skipif(
       len(_devices) == 0,
       reason="no devices with ID_SAS_PATH property"
    )
    @given(strategies.sampled_from(_devices))
    @settings(min_satisfying_examples=1)
    def test_parsing_sas_path(self, a_device):
        """
        Test that parsing is satisfactory on all examples.
        """
        parsers = _parsing.IdPathParsers.PARSERS
        id_path = a_device.get('ID_SAS_PATH')
        parser = _parsing.IdPathParse(parsers)
        result = parser.parse(id_path)
        assert isinstance(result, list) and result != []
        assert all(
           any(r[1].group('total').startswith(p.prefix) for p in parsers) \
                   for r in result
        )
        assert not any(r[1].group('total').startswith('-') for r in result)

    def test_failure(self):
        """
        Test at least one failure.
        """
        id_path = 'pci-0000_09_00_0-sas0x5000155359566200-lun-0'
        parser = _parsing.IdPathParse(_parsing.IdPathParsers.PARSERS)
        result = parser.parse(id_path)
        assert result == []


class TestDevlinks(object):
    """
    Test ``Devlinks`` methods.
    """
    # pylint: disable=too-few-public-methods

    _devices = [d for d in _DEVICES if list(d.device_links)]
    @pytest.mark.skipif(
       len(_devices) == 0,
       reason="no devices with device links"
    )
    @given(strategies.sampled_from(_devices))
    @settings(max_examples=5, min_satisfying_examples=1)
    def test_devlinks(self, a_device):
        """
        Verify that device links are in "by-.*" categories or no category.
        """
        device_links = (_parsing.Devlink(d) for d in a_device.device_links)

        def sort_func(dl):
            """
            :returns: category of device link
            :rtype: str
            """
            key = dl.category
            return key if key is not None else ""

        devlinks = sorted(device_links, key=sort_func)

        categories = list(k for k, g in groupby(devlinks, sort_func))
        assert all(c == "" or c.startswith("by-") for c in categories)

        assert all((d.category is None and d.value is None) or \
           (d.category is not None and d.value is not None) \
           for d in devlinks)

        assert all(d.path == str(d) for d in devlinks)


class TestPCIAddress(object):
    """
    Test parsing a PCI address object.
    """
    # pylint: disable=too-few-public-methods

    _devices = [d for d in _DEVICES if d.subsystem == 'pci']
    @pytest.mark.skipif(
       len(_devices) == 0,
       reason="no devices with subsystem pci"
    )
    @given(strategies.sampled_from(_devices))
    @settings(min_satisfying_examples=1)
    def test_parsing_pci(self, a_device):
        """
        Test correct parsing of pci-addresses.
        """
        (parser, result) = _parsing.PCIAddressParse().parse(a_device.sys_name)
        assert all(result.group(k) != "" for k in parser.keys)
