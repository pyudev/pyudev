#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2010, 2011, 2012 Sebastian Wiesner <lunaryorn@googlemail.com>

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


import sys
try:
    import setuptools
except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()
    import setuptools

from setuptools.command.build_py import build_py
import setuptools.command.build_py

import pyudev

def find_fixers(blacklist=None):
    blacklist = blacklist or []
    names = getattr(build_py, 'fixer_names', None) or []
    from lib2to3.refactor import get_fixers_from_package
    for p in setuptools.lib2to3_fixer_packages:
        names.extend(get_fixers_from_package(p))
    # explicitly remove all blacklisted fixers to trigger value errors on
    # non-existing filters in the blacklist
    for f in blacklist:
        names.remove(f)
    build_py.fixer_names = names

if sys.version_info[0] < 3:
    from codecs import open
    extra_arguments = {}
else:
    # Remove import fixer, because it blews up absolute imports on some python
    # versions, see Python bug #8358
    find_fixers(blacklist=['lib2to3.fixes.fix_import'])
    extra_arguments = dict(use_2to3=True)


with open('README.rst', encoding='utf-8') as stream:
    long_description = stream.read()


setuptools.setup(
    name='pyudev',
    version=str(pyudev.__version__),
    url='http://pyudev.readthedocs.org/',
    author='Sebastian Wiesner',
    author_email='lunaryorn@googlemail.com',
    description='A libudev binding',
    long_description=long_description,
    platforms=['Linux'],
    license='MIT/X11',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Hardware',
        'Topic :: System :: Operating System Kernels :: Linux',
        ],
    packages=setuptools.find_packages(),
    **extra_arguments
    )
