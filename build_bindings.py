# -*- coding: utf-8 -*-
# Copyright (C) 2012 Sebastian Wiesner <lunaryorn@gmail.com>

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
    build_bindings
    ==============

    Script to build native bindings inside virtualenvs.

    This plugin builds pygobject, PyQt4.QtCore, PySide.QtCore and wxPython if
    these are not available.

    This feature is mainly intented for use with tox_, but can be used in
    normal virtualenvs, too.

    .. warning::

       The directory pointed to by ``os.path.join(sys.prefix, 'lib')`` must be
       contained in the load path of shared libraries, otherwise bindings may
       fail to load.  The tox_ configuration of pyudev implicitly sets
       ``LD_LIBRARY_PATH`` accordingly, but in your own virtual environments
       you need to do this yourself.  A convenient way to accomplish this is
       virtualenvwrapper_.

    .. _tox: http://tox.testrun.org
    .. _virtualenvwrapper: http://www.doughellmann.com/projects/virtualenvwrapper/

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@gmail.com>
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import sys
import platform
import os
import posixpath
import errno
from collections import defaultdict
from subprocess import call, check_call
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

import py.path


IS_CPYTHON = platform.python_implementation() == 'CPython'


class MissingDependencyError(Exception):
    pass


class MissingProgramError(KeyError):
    pass


def ensure_directory(directory):
    try:
        os.makedirs(directory)
    except EnvironmentError as error:
        if error.errno != errno.EEXIST:
            raise


class Programs(defaultdict):

    def __missing__(self, key):
        path = py.path.local.sysfind(key)
        if not path:
            raise MissingProgramError(key)
        return str(path)


class Environment(object):

    def __init__(self, download_directory, build_directory):
        self.download_directory = download_directory
        self.build_directory = build_directory
        self.programs = Programs()
        # a basic build environment
        self.environ = dict(os.environ)
        self.environ['LD_LIBRARY_PATH'] = os.path.join(
            sys.prefix, 'lib')
        self.environ['PKG_CONFIG_PATH'] = os.path.join(
            sys.prefix, 'lib', 'pkgconfig')

    def prepare(self):
        ensure_directory(self.download_directory)
        ensure_directory(self.build_directory)

    def build(self, binding, force=False):
        binding(self, force=force).install()

    def build_all(self, bindings, force=False):
        for binding in bindings:
            self.build(binding, force=force)


def have_module(modname):
    try:
        __import__(modname)
        return True
    except ImportError:
        return False


class Binding(object):

    DEPENDS = []

    def __init__(self, env, force=False):
        self.env = env
        self.build_directory = os.path.join(env.build_directory, self.NAME)
        self.force = force

    @property
    def is_installed(self):
        raise NotImplementedError()

    @property
    def can_build(self):
        return IS_CPYTHON

    @property
    def source_archive(self):
        filename = posixpath.basename(urlparse(self.SOURCE_URL).path)
        return os.path.join(self.env.download_directory, filename)

    @property
    def build_environment(self):
        return dict(self.env.environ)

    @property
    def number_of_builds(self):
        # build on all cores if possible
        try:
            from multiprocessing import cpu_count
            return cpu_count()
        except (NotImplementedError, ImportError):
            return 1

    def have_pkg_config_package(self, package):
        command = [self.env.programs['pkg-config'], '--exists', package]
        return call(command, env=self.env.environ) == 0

    def find_dependencies(self):
        return

    def check_call(self, command):
        check_call(command, cwd=self.build_directory,
                   env=self.build_environment)

    def download(self):
        call([self.env.programs['wget'], '-c',
              '-O', self.source_archive, self.SOURCE_URL])

    def extract(self):
        check_call([self.env.programs['tar'], 'xaf', self.source_archive,
                    '-C', os.path.dirname(self.build_directory)])

    def prepare(self):
        self.download()
        self.extract()
        self.find_dependencies()

    def install(self):
        if self.is_installed and not self.force:
            return
        self.env.build_all(self.DEPENDS)
        if not self.can_build:
            return
        self.prepare()
        self.build()

    def build(self):
        raise NotImplementedError()

    def make(self, target=None):
        command = [self.env.programs['make'],
                   '-j{0}'.format(self.number_of_builds)]
        if target:
            command.append(target)
        self.check_call(command)

    def make_build_and_install(self):
        self.make()
        self.make('install')


class AutotoolsBinding(Binding):

    CONFIGURE_EXTRA_ARGS = []

    @property
    def build_environment(self):
        # tell autotools where to find the Python interpreter
        env = dict(self.env.environ)
        # autotools needs the flat name of the python interpreter to discover
        # the headers
        python = os.path.basename(sys.executable)
        # append version number if the interpreter executable doesn't have one,
        # to avoid ambiguities between virtualenv python and system python
        if not python[-1].isdigit():
            python += '{0}.{1}'.format(*sys.version_info)
        env['PYTHON'] = python
        return env

    def autotools_configure(self, extra_args):
        command = ['./configure', '--prefix', sys.prefix] + extra_args
        self.check_call(command)

    def build(self):
        self.autotools_configure(self.CONFIGURE_EXTRA_ARGS)
        self.make_build_and_install()


class PyGObject(AutotoolsBinding):
    NAME = 'pygobject-2.28.6'
    SOURCE_URL = ('http://ftp.gnome.org/pub/GNOME/sources/pygobject/2.28/'
                  '{0}.tar.bz2'.format(NAME))

    CONFIGURE_EXTRA_ARGS = ['--disable-introspection']

    @property
    def is_installed(self):
        return have_module('glib') and have_module('gobject')


RIVERBANK_DOWNLOADS = 'http://www.riverbankcomputing.com/static/Downloads'


class Sip4(Binding):
    NAME = 'sip-4.13.3'
    SOURCE_URL = '{0}/sip4/{1}.tar.gz'.format(RIVERBANK_DOWNLOADS, NAME)

    @property
    def is_installed(self):
        return have_module('sip')

    def build(self):
        incdir = os.path.join(sys.prefix, 'include', 'sip')
        self.check_call([sys.executable, 'configure.py', '--incdir', incdir])
        self.make_build_and_install()


class PyQt4QtCore(Binding):
    NAME = 'PyQt-x11-gpl-4.9.4'
    SOURCE_URL = '{0}/PyQt4/{1}.tar.gz'.format(RIVERBANK_DOWNLOADS, NAME)

    DEPENDS = [Sip4]

    @property
    def is_installed(self):
        return have_module('PyQt4.QtCore')

    def find_dependencies(self):
        try:
            self.qmake = self.env.programs['qmake-qt4']
        except KeyError:
            self.qmake = self.env.programs['qmake']

    def build(self):
        command = [sys.executable, 'configure.py', '--confirm-license',
                   '--no-designer-plugin', '--no-sip-files', '--no-qsci-api',
                   '--qmake', self.qmake, '--enable', 'QtCore']
        self.check_call(command)
        self.make_build_and_install()


class CMakeBinding(Binding):
    CMAKE_EXTRA_ARGS = []

    def cmake_configure(self, extra_args):
        # cmake uses out of source builds
        self.build_directory = os.path.join(self.build_directory, 'build')
        ensure_directory(self.build_directory)
        command = [self.env.programs['cmake'],
                   '-DBUILD_TESTS=OFF', '-DCMAKE_BUILD_TYPE=RelWithDebInfo',
                   '-DCMAKE_INSTALL_PREFIX={0}'.format(sys.prefix)]
        command += extra_args
        command += ['..']
        self.check_call(command)

    def build(self):
        self.cmake_configure(self.CMAKE_EXTRA_ARGS)
        self.make_build_and_install()


PYSIDE_DOWNLOADS = 'http://www.pyside.org/files'


class Shiboken(CMakeBinding):
    NAME = 'shiboken-1.1.1'
    SOURCE_URL = '{0}/{1}.tar.bz2'.format(PYSIDE_DOWNLOADS, NAME)

    CMAKE_EXTRA_ARGS = [
        '-DPython_ADDITIONAL_VERSIONS={0}.{1}'.format(*sys.version_info)
    ]

    if sys.version_info[0] == 3:
        CMAKE_EXTRA_ARGS += ['-DUSE_PYTHON3=ON']

    @property
    def is_installed(self):
        return self.have_pkg_config_package('shiboken')


DISABLED_QT_MODULES = [
    'QtGui', 'QtMultimedia', 'QtNetwork', 'QtOpenGL',
    'QtScript', 'QtScriptTools', 'QtSql', 'QtSvg', 'QtWebKit',
    'QtXml', 'QtXmlPatterns', 'QtDeclarative', 'phonon',
    'QtUiTools', 'QtHelp', 'QtTest']


class PySideQtCore(CMakeBinding):
    NAME = 'pyside-qt4.7+1.1.1'
    SOURCE_URL = '{0}/{1}.tar.bz2'.format(PYSIDE_DOWNLOADS, NAME)

    DEPENDS = [Shiboken]

    CMAKE_EXTRA_ARGS = ['-DDISABLE_{0}=ON'.format(mod)
                        for mod in DISABLED_QT_MODULES]

    @property
    def is_installed(self):
        return have_module('PySide.QtCore')


class WxPython(Binding):
    NAME = 'wxPython-src-2.8.12.1'
    SOURCE_URL = ('http://downloads.sourceforge.net/wxpython/'
                  '{0}.tar.bz2'.format(NAME))

    @property
    def can_build(self):
        # wx doesn't support Python 3
        return IS_CPYTHON and sys.version_info[0] == 2

    @property
    def is_installed(self):
        return have_module('wx')

    def build(self):
        self.build_directory = os.path.join(
            self.build_directory, 'wxPython')
        cmd = [sys.executable, 'setup.py', 'WXPORT=gtk2', 'UNICODE=1',
               # need to invoke install commands individually, because
               # "install" invokes "install_headers" which insists on
               # installing headers to system directories despite of a
               # virtualenv prefix.  Praise wx…
               'build', 'install_lib', 'install_data']
        self.check_call(cmd)


AVAILABLE_BINDINGS = {
    'pyqt4': PyQt4QtCore,
    'pyside': PySideQtCore,
    'pygobject': PyGObject,
    'wxpython': WxPython,
}


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-d', '--download-directory',
                        help='Download directory')
    parser.add_argument('-b', '--build-directory', help='Build directory')
    parser.add_argument('-f', '--force-build', action='store_true',
                        help='Build even if the binding is already available')
    parser.add_argument('--binding', action='append', dest='bindings',
                        help='Binding to build', choices=AVAILABLE_BINDINGS)
    parser.set_defaults(download_directory='/tmp/pyudev-build-bindings',
                        build_directory='/tmp/pyudev-build-bindings')

    args = parser.parse_args()
    if not args.bindings:
        args.bindings = AVAILABLE_BINDINGS.keys()

    bindings = [AVAILABLE_BINDINGS[b] for b in args.bindings]

    env = Environment(args.download_directory, args.build_directory)
    env.prepare()
    env.build_all(bindings, force=args.force_build)


if __name__ == '__main__':
    main()
