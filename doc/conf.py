# -*- coding: utf-8 -*-
# Copyright (C) 2010, 2011 Sebastian Wiesner <lunaryorn@googlemail.com>

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

import sys, os

doc_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.normpath(
    os.path.join(doc_directory, os.pardir)))

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
html_domain_indices = ['py-modindex']

intersphinx_mapping = {'python': ('http://docs.python.org/', None)}

issuetracker = 'github'
issuetracker_user = 'lunaryorn'


def setup(app):
    from sphinx.ext.autodoc import cut_lines
    app.connect(b'autodoc-process-docstring', cut_lines(2, what=['module']))
