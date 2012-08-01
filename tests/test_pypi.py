# -*- coding: utf-8 -*-
# Copyright (C) 2010, 2011, 2012 Sebastian Wiesner <lunaryorn@gmail.com>

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


from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import re
import os
import subprocess
from distutils.filelist import FileList

import py.path
import pytest


TEST_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIRECTORY = os.path.abspath(os.path.join(
    TEST_DIRECTORY, os.pardir))
MANIFEST = os.path.join(SOURCE_DIRECTORY, 'MANIFEST.in')


# Files in the repository that don't need to be present in the sdist
REQUIRED_BLACKLIST = [r'^\.git.+', r'\.travis\.yml$', r'^MANIFEST\.in$']


def _get_required_files():
    if not os.path.isdir(os.path.join(SOURCE_DIRECTORY, '.git')):
        pytest.skip('Not in git clone')
    git = py.path.local.sysfind('git')
    if not git:
        pytest.skip('git not available')
    ls_files = subprocess.Popen(['git', 'ls-files'], cwd=SOURCE_DIRECTORY,
                                stdout=subprocess.PIPE)
    output = ls_files.communicate()[0]
    for filename in output.splitlines():
        if not any(re.search(p, filename) for p in REQUIRED_BLACKLIST):
            yield filename


def _get_manifest_files():
    filelist = FileList()
    old_wd = os.getcwd()
    try:
        os.chdir(SOURCE_DIRECTORY)
        filelist.findall()
    finally:
        os.chdir(old_wd)
    with open(MANIFEST, 'r') as source:
        for line in source:
            filelist.process_template_line(line.strip())
    return filelist.files


def test_manifest_complete():
    required_files = sorted(_get_required_files())
    included_files = sorted(_get_manifest_files())
    assert required_files == included_files
