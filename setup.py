#!/usr/bin/python
# -*- coding: utf-8 -*-


from setuptools import setup


with open('README.rst') as stream:
    long_description = stream.read().decode('utf-8')


setup(
    name='pyudev',
    version='0.1',
    url='http://packages.python.org/pyudev',
    author='Sebastian Wiesner',
    author_email='lunaryorn@googlemail.com',
    description='A libudeb binding',
    long_description=long_description,
    license='MIT/X11',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Hardware',
        'Topic :: System :: Operating System Kernels :: Linux',
        ],
    py_modules=['udev', '_udev'],
    )
