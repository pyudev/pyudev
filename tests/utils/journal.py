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
    utils.journal
    =============

    Provide access to journal entries.

    Note that no current version of systemd is available from pypi.
    When running on Python specific testing frameworks, need to fall
    back on pyjournalctl package.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals



try:
    from systemd import journal

    def journal_entries():
        """
        A sequence of journal entries.
        """
        with journal.Reader() as reader:
            reader.this_boot()
            for entry in reader:
                yield entry
except ImportError:
    def journal_entries():
        """
        Proper version of systemd is not available, so yield no entries.
        """
        if False:
            yield None
