# -*- coding: utf-8 -*-

import sys, os

import pyudev

needs_sphinx = '1.0'

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx',
              'sphinxcontrib.pyqt4', 'sphinxcontrib.issuetracker']

master_doc = 'index'
exclude_patterns = ['_build/*']
source_suffix = '.rst'

project = u'pyudev'
copyright = u'2010, Sebastian Wiesner'
version = '.'.join(pyudev.__version__.split('.')[:2])
release = pyudev.__version__

html_theme = 'default'
html_static_path = []

intersphinx_mapping = {'python': ('http://docs.python.org/', None)}

issuetracker = 'github'
issuetracker_user = u'lunaryorn'


def setup(app):
    from sphinx.ext.autodoc import cut_lines
    app.connect('autodoc-process-docstring', cut_lines(2, what=['module']))
