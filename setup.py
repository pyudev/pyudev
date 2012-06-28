#!/usr/bin/python
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


import sys
import setuptools
if sys.version_info[0] < 3:
    from codecs import open

import pyudev

with open('README.rst', encoding='utf-8') as stream:
    long_description = stream.read()


setuptools.setup(
    name='pyudev',
    version=str(pyudev.__version__),
    url='http://pyudev.readthedocs.org/',
    author='Sebastian Wiesner',
    author_email='lunaryorn@gmail.com',
    description='A libudev binding',
    long_description=long_description,
    platforms=['Linux'],
    license='LGPL 2.1+',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Hardware',
        'Topic :: System :: Operating System Kernels :: Linux',
        ],
    packages=setuptools.find_packages(),
    )
