#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2010, 2011 Sebastian Wiesner <lunaryorn@googlemail.com>

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.


"""
    bootstrap_native_bindings
    =========================

    Bootstrapping script for native bindings used during pyudev tests.

    This code is executed from *inside* the virtual environment created by
    tox and must therefore run on Python 2 *as well* as on Python 3.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""


from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import sys
import os
import errno
import posixpath
import subprocess
import logging
import platform
from optparse import OptionParser
from collections import namedtuple


class MissingDependency(Exception):

    def __str__(self):
        return '{0} is missing'.format(self.args[0])


class SubprocessMixin(object):
    def _check_call(self, command, **options):
        self.log.debug('calling %r with options %r', command, options)
        subprocess.check_call(command, **options)


def ensuredirs(*directories):
    for directory in directories:
        try:
            os.makedirs(directory)
        except EnvironmentError as error:
            if error.errno != errno.EEXIST:
                raise


class SourcePackage(namedtuple(
    '_SourcePackage', 'name version buildtype url_template'),
                    SubprocessMixin):

    log = logging.getLogger('bootstrap.source')

    @property
    def url(self):
        return self.url_template.format(**self._asdict())

    def download(self, target_directory):
        filename = posixpath.basename(self.url)
        target = os.path.join(target_directory, filename)
        if not os.path.isfile(target):
            try:
                self.log.info('downloading %s to %s', self.url, target)
                self._check_call(['wget', '-O', target, self.url])
            except:
                if os.path.isfile(target):
                    os.unlink(target)
                raise
        else:
            self.log.info('skipping %s, already downloaded', self.url)
        return target

    def make_build(self, download_directory, target_directory):
        archive = self.download(download_directory)
        self.log.info('extracting %s to %s', archive, target_directory)
        self._check_call(['tar', '-x', '-a', '-f', archive,
                          '-C', target_directory])
        return self.buildtype(os.path.join(
            target_directory, '{0.name}-{0.version}'.format(self)))

    def build(self, download_directory, target_directory):
        self.make_build(download_directory, target_directory).run()


class Build(SubprocessMixin):
    def __init__(self, source_directory):
        self.log = logging.getLogger('bootstrap.builder')
        self.source_directory = source_directory

    def _check_program(self, program):
        try:
            with open(os.devnull, 'wb') as devnull:
                self._check_call([program, '--version'], stdout=devnull)
        except EnvironmentError:
            raise MissingDependency(program)

    def _check_package(self, package):
        self._check_program('pkg-config')
        try:
            self._check_call(['pkg-config', '--exists', package])
        except subprocess.CalledProcessError:
            raise MissingDependency(package)

    @property
    def build_directory(self):
        return self.source_directory

    def ensure_dependencies(self):
        self._check_program('make')

    def initialize(self):
        pass

    def configure(self):
        pass

    def build(self):
        self.log.info('building in %s', self.build_directory)
        self._check_call(['make'], cwd=self.build_directory)

    def install(self):
        self.log.info('installing from %s', self.build_directory)
        self._check_call(['make', 'install'],
                         cwd=self.build_directory)

    def run(self):
        try:
            self.ensure_dependencies()
        except MissingDependency as missing:
            print(missing)
        else:
            self.initialize()
            self.configure()
            self.build()
            self.install()

    def __call__(self):
        self.run()


class SipBuild(Build):

    configure_options = [
        '--incdir', os.path.join(sys.prefix, 'include', 'sip')]

    def configure(self):
        self.log.info('configuring in %s with %r', self.build_directory,
                      self.configure_options)
        cmd = [sys.executable, 'configure.py']
        cmd.extend(self.configure_options)
        self._check_call(cmd, cwd=self.build_directory)


class PyQtBuild(SipBuild):
    configure_options = ['--confirm-license', '--concatenate',
                         '--enable', 'QtCore',
                         '--no-designer-plugin', '--no-sip-files',
                         '--no-qsci-api']

    def ensure_dependencies(self):
        SipBuild.ensure_dependencies(self)
        self._check_package('QtCore')


class CMakeBuild(Build):

    configure_options = ['-DBUILD_TESTS=OFF',
                         '-DPython_ADDITIONAL_VERSIONS={0}.{1}'.format(
                             *sys.version_info)]

    def ensure_dependencies(self):
        Build.ensure_dependencies(self)
        self._check_program('cmake')

    @property
    def build_directory(self):
        return os.path.join(self.source_directory, 'build')

    def initialize(self):
        self.log.info('creating build directory')
        ensuredirs(self.build_directory)

    def configure(self):
        self.log.info('configuring in %s', self.build_directory)
        cmd = ['cmake', '-DCMAKE_INSTALL_PREFIX={0}'.format(sys.prefix),
               '-DCMAKE_BUILD_TYPE=RelWithDebInfo']
        cmd.extend(self.configure_options)
        cmd.append(os.path.abspath(self.source_directory))
        self._check_call(cmd, cwd=self.build_directory)


class PySideBuild(CMakeBuild):
    configure_options = CMakeBuild.configure_options + [
        '-DDISABLE_{0}=ON'.format(mod) for mod in
        ('QtGui', 'QtMultimedia', 'QtNetwork', 'QtOpenGL', 'QtScript',
         'QtScriptTools', 'QtSql', 'QtSvg', 'QtWebKit', 'QtXml',
         'QtXmlPatterns', 'QtDeclarative', 'phonon', 'QtUiTools', 'QtHelp',
         'QtTest')]

    def ensure_dependencies(self):
        CMakeBuild.ensure_dependencies(self)
        self._check_package('QtCore')


class AutotoolsBuild(Build):
    configure_options = ['--prefix', sys.prefix]

    def configure(self):
        self.log.info('configuring %s with %r', self.build_directory,
                      self.configure_options)
        cmd = ['./configure']
        cmd.extend(self.configure_options)
        self._check_call(cmd, cwd=self.build_directory)


class PyGObjectBuild(AutotoolsBuild):
    configure_options = AutotoolsBuild.configure_options + [
        '--disable-dependency-tracking']

    def ensure_dependencies(self):
        AutotoolsBuild.ensure_dependencies(self)
        self._check_package('gobject-2.0')
        self._check_package('gio-2.0')
        self._check_package('gobject-introspection-1.0')


RIVERBANK_DOWNLOAD_URL = 'http://www.riverbankcomputing.com/static/Downloads/{0}'

PYQT4_SOURCES = [
    SourcePackage('sip', '4.12.3', SipBuild,
                  RIVERBANK_DOWNLOAD_URL.format(
                      'sip4/{name}-{version}.tar.gz')),
    SourcePackage('PyQt-x11-gpl', '4.8.4', PyQtBuild,
                  RIVERBANK_DOWNLOAD_URL.format(
                      'PyQt4/{name}-{version}.tar.gz'))]

PYSIDE_DOWNLOAD_URL = 'http://www.pyside.org/files/{0}'

PYSIDE_SOURCES = [
    SourcePackage('apiextractor', '0.10.3', CMakeBuild,
                  PYSIDE_DOWNLOAD_URL.format('{name}-{version}.tar.bz2')),
    SourcePackage('generatorrunner', '0.6.10', CMakeBuild,
                  PYSIDE_DOWNLOAD_URL.format('{name}-{version}.tar.bz2')),
    SourcePackage('shiboken', '1.0.3', CMakeBuild,
                  PYSIDE_DOWNLOAD_URL.format('{name}-{version}.tar.bz2')),
    SourcePackage('pyside', 'qt4.7+1.0.3', PySideBuild,
                  PYSIDE_DOWNLOAD_URL.format('{name}-{version}.tar.bz2')),
    ]

GNOME_DOWNLOAD_URL = 'http://ftp.gnome.org/pub/GNOME/sources/{0}'

GOBJECT_SOURCES = [
    SourcePackage('pygobject', '2.26.0', PyGObjectBuild,
                  GNOME_DOWNLOAD_URL.format(
                      '{name}/2.26/{name}-{version}.tar.bz2'))]


def build_all(sources, download_directory, build_directory):
    for source in sources:
        source.build(download_directory, build_directory)


def import_string(import_name, silent=False):
    """
    Import an object based on a string given by ``import_name``.  An import
    path can be specified either in dotted notation
    (``'xml.sax.saxutils.escape'``) or with a colon as object delimiter
    (``'xml.sax.saxutils:escape'``).

    Return the imported object.  If the import or the attribute access fails
    and ``silent`` is ``True``, ``None`` will be returned.  Otherwise
    :exc:`~exceptions.ImportError` or :exc:`~exceptions.AttributeError` will
    be raised.

    This function was shamelessly stolen from Werkzeug_.  Thanks to Armin
    Ronacher.

    .. _werkzeug: http://werkzeug.pocoo.org
    """
    try:
        if ':' in import_name:
            module, obj = import_name.split(':', 1)
        elif '.' in import_name:
            module, obj = import_name.rsplit('.', 1)
        else:
            return __import__(import_name)
        # to make things run on python 2 and python 3
        obj = str(obj)
        module = str(module)
        return getattr(__import__(module, None, None, [obj]), obj)
    except (ImportError, AttributeError):
        if not silent:
            raise


def have_pyqt4_qtcore(expected_version):
    log = logging.getLogger('pyqt4')
    try:
        QtCore = import_string('PyQt4.QtCore')
        log.info('excepted version %s, actual version %s',
                 expected_version, QtCore.PYQT_VERSION_STR)
        return QtCore.PYQT_VERSION_STR == expected_version
    except ImportError:
        log.exception('QtCore not found')
        return False


def have_pyside_qtcore(expected_version):
    log = logging.getLogger('pyside')
    try:
        import_string('PySide.QtCore')
        PySide = import_string('PySide')
        log.info('excepted version %s, actual version %s',
                 expected_version, PySide.__version__)
        return PySide.__version__ == expected_version
    except ImportError:
        log.exception('QtCore not found')
        return False


def have_gobject(expected_version):
    log = logging.getLogger('pygobject')
    expected_version = tuple(map(int, expected_version.split('.')[:3]))
    for libname in ('glib', 'gobject'):
        try:
            lib = import_string(libname)
            version_attr = 'py{0}_version'.format(libname)
            lib_version = getattr(lib, version_attr)
            log.info('%s: expected version %s, actual version %s',
                     libname, expected_version, lib_version)
            if lib_version < expected_version:
                return False
        except ImportError:
            log.exception('%s not found', libname)
            return False
    return True


def main():
    parser = OptionParser(usage='%prog download_directory build_directory')
    parser.add_option('--debug', action='store_const', dest='loglevel',
                      const=logging.DEBUG)
    parser.add_option('--verbose', action='store_const', dest='loglevel',
                      const=logging.INFO)
    parser.set_defaults(loglevel=logging.WARN)
    opts, args = parser.parse_args()
    if len(args) != 2:
        parser.error('missing arguments')
    logging.basicConfig(level=opts.loglevel)

    if platform.python_implementation() != 'CPython':
        return

    try:
        download_directory, build_directory = args
        ensuredirs(download_directory, build_directory)

        if not have_pyqt4_qtcore(PYQT4_SOURCES[1].version):
            build_all(PYQT4_SOURCES, download_directory, build_directory)

        if sys.version_info[0] < 3:
            # pyside and pygobject are not available for python 3 yet
            if not have_pyside_qtcore(PYSIDE_SOURCES[3].version.split('+')[1]):
                build_all(PYSIDE_SOURCES, download_directory, build_directory)

            if not have_gobject(GOBJECT_SOURCES[0].version):
                build_all(GOBJECT_SOURCES, download_directory, build_directory)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
