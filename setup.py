#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
if sys.version_info[0] < 3:
    from codecs import open
    extra_arguments = {}
else:
    extra_arguments = dict(use_2to3=True)

try:
    from setuptools import setup, find_packages
except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()
    from setuptools import setup, find_packages

import pyudev

with open('README.rst', encoding='utf-8') as stream:
    long_description = stream.read()


setup(
    name='pyudev',
    version=pyudev.__version__,
    url='http://packages.python.org/pyudev',
    author='Sebastian Wiesner',
    author_email='lunaryorn@googlemail.com',
    description='A libudev binding',
    long_description=long_description,
    platforms='Linux',
    license='MIT/X11',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Hardware',
        'Topic :: System :: Operating System Kernels :: Linux',
        ],
    install_requires=['apipkg>=1.0b6'],
    packages=find_packages(),
    **extra_arguments
    )
