# -*- coding: utf-8 -*-

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
copyright = u'2010, Sebastian Wiesner'
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
    app.connect('autodoc-process-docstring', cut_lines(2, what=['module']))
