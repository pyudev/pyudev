# -*- coding: utf-8 -*-
# Copyright (c) 2010 Sebastian Wiesner <lunaryorn@googlemail.com>

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


import sys
import os
import errno
import posixpath
import subprocess
from optparse import OptionParser


SIP_VERSION = '4.11.1'
PYQT4_VERSION = '4.7.6'


class BuildEnvironment(object):
    def __init__(self, download_directory, build_directory):
        self.download_directory = download_directory
        self.build_directory = build_directory
        try:
            os.makedirs(self.build_directory)
        except EnvironmentError as error:
            if error.errno != errno.EEXIST:
                raise

    def download(self, url):
        filename = posixpath.basename(url)
        destination = os.path.join(self.download_directory, filename)
        if not os.path.isfile(destination):
            subprocess.check_call(['curl', '-o', destination, url])
        return destination

    def extract_source_archive(self, archive):
        subprocess.check_call(['tar', 'xzf', archive, '-C',
                               self.build_directory])


def have_pyqt4_qtcore():
    try:
        QtCore = __import__('PyQt4.QtCore', globals(), locals(), ['QtCore'])
        return QtCore.PYQT_VERSION_STR == PYQT4_VERSION
    except ImportError:
        return False


def configure_directory(directory, *opts):
    cmd = [sys.executable, 'configure.py']
    cmd.extend(opts)
    subprocess.check_call(cmd, cwd=directory)


def make_install(directory):
    subprocess.check_call(['make'], cwd=directory)
    subprocess.check_call(['make', 'install'], cwd=directory)


def install_sip(env):
    url = 'http://www.riverbankcomputing.com/static/Downloads/sip4/sip-{0}.tar.gz'
    source_archive = env.download(url.format(SIP_VERSION))
    env.extract_source_archive(source_archive)
    build_directory = os.path.join(env.build_directory,
                                   'sip-{0}'.format(SIP_VERSION))
    configure_directory(
        build_directory, '--incdir',
        os.path.join(sys.prefix, 'include', 'sip'))
    make_install(build_directory)


def install_pyqt4_qtcore(env):
    url = 'http://www.riverbankcomputing.com/static/Downloads/PyQt4/PyQt-x11-gpl-{0}.tar.gz'
    source_archive = env.download(url.format(PYQT4_VERSION))
    env.extract_source_archive(source_archive)
    build_directory = os.path.join(env.build_directory,
                                   'PyQt-x11-gpl-{0}'.format(PYQT4_VERSION))
    configure_directory(
        build_directory, '--confirm-license', '--concatenate',
        '--enable', 'QtCore', '--no-designer-plugin', '--no-sip-files',
        '--no-qsci-api')
    make_install(build_directory)


def main():
    parser = OptionParser(usage='%prog download_directory build_directory')
    opts, args = parser.parse_args()
    if len(args) != 2:
        parser.error('missing arguments')
    download_directory, build_directory = args
    env = BuildEnvironment(download_directory, build_directory)
    if not have_pyqt4_qtcore():
        install_sip(env)
        install_pyqt4_qtcore(env)


if __name__ == '__main__':
    main()
