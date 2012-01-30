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


from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import sys
import os

from docutils import nodes
from docutils.parsers.rst import Directive

# add the pyudev source directory to our path
doc_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.normpath(
    os.path.join(doc_directory, os.pardir)))


class Mock(object):
    """
    Mock modules.

    Taken from
    http://read-the-docs.readthedocs.org/en/latest/faq.html#i-get-import-errors-on-libraries-that-depend-on-c-modules
    with some slight changes.
    """

    @classmethod
    def mock_modules(cls, *modules):
        for module in modules:
            sys.modules[module] = cls()

    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return self.__class__()

    def __getattr__(self, attribute):
        if attribute in ('__file__', '__path__'):
            return os.devnull
        else:
            # return the *class* object here.  Mocked attributes may be used as
            # base class in pyudev code, thus the returned mock object must
            # behave as class, or else Sphinx autodoc will fail to recognize
            # the mocked base class as such, and "autoclass" will become
            # meaningless
            return self.__class__


# mock out native modules used throughout pyudev to enable Sphinx autodoc even
# if these modules are unavailable, as on readthedocs.org
Mock.mock_modules('PyQt4', 'PyQt4.QtCore', 'PySide', 'PySide.QtCore',
                  'glib', 'gobject', 'wx', 'wx.lib', 'wx.lib.newevent',
                  'pyudev._libudev')

# mock out the NewEvent function of wxPython.  Let's praise the silly wx API
def NewEventMock():
    yield 'event_class'
    yield 'event_constant'

sys.modules['wx.lib.newevent'].NewEvent = NewEventMock


import pyudev

needs_sphinx = '1.0'

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx',
              'sphinxcontrib.issuetracker']

master_doc = 'index'
exclude_patterns = ['_build/*']
source_suffix = '.rst'

project = u'pyudev'
copyright = u'2010, 2011 Sebastian Wiesner'
version = '.'.join(pyudev.__version__.split('.')[:2])
release = pyudev.__version__

html_theme = 'default'
html_static_path = []

intersphinx_mapping = {'python': ('http://docs.python.org/', None),
                       'pyside': ('http://www.pyside.org/docs/pyside/', None)}

issuetracker = 'github'
issuetracker_project = 'lunaryorn/pyudev'


class UDevVersion(Directive):
    """
    Directive to document the minimum udev version to use an attribute or
    method
    """
    has_content = False
    required_arguments = 1
    option_spec = {}

    def run(self):
        udevversion = self.arguments[0]
        para = nodes.paragraph(udevversion, '', classes=['udevversion'])
        text = 'Required udev version: {0}'.format(*self.arguments)
        para.append(nodes.inline(udevversion, text, classes=['versionmodified']))
        return [para]


def setup(app):
    from sphinx.ext.autodoc import cut_lines
    app.connect(b'autodoc-process-docstring', cut_lines(2, what=['module']))
    app.add_directive('udevversion', UDevVersion)
