# -*- coding: utf-8 -*-
# Copyright (C) 2010, 2011, 2012, 2013 Sebastian Wiesner <lunaryorn@gmail.com>

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

# isort: FUTURE
from __future__ import absolute_import, division, print_function, unicode_literals

# isort: STDLIB
import os
import re
import subprocess
import sys
from distutils.filelist import FileList

# isort: THIRDPARTY
import py.path
import pytest
from docutils import io, readers
from docutils.core import Publisher, publish_doctree
from docutils.transforms import TransformError

if sys.version_info[0] < 3:
    from codecs import open
    from urlparse import urlparse


TEST_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIRECTORY = os.path.abspath(os.path.join(TEST_DIRECTORY, os.pardir))
MANIFEST = os.path.join(SOURCE_DIRECTORY, "MANIFEST.in")
README = os.path.join(SOURCE_DIRECTORY, "README.rst")

# Files in the repository that don't need to be present in the sdist
REQUIRED_BLACKLIST = [r"^\.git.+", r"\.travis\.yml$", r"^MANIFEST\.in$", r"^Makefile$"]


def _get_required_files():
    if not os.path.isdir(os.path.join(SOURCE_DIRECTORY, ".git")):
        pytest.skip("Not in git clone")
    git = py.path.local.sysfind("git")
    if not git:
        pytest.skip("git not available")
    ls_files = subprocess.Popen(
        ["git", "ls-files"], cwd=SOURCE_DIRECTORY, stdout=subprocess.PIPE
    )
    output = ls_files.communicate()[0].decode("utf-8")
    for filename in output.splitlines():
        if not any(re.search(p, filename) for p in REQUIRED_BLACKLIST):
            yield filename


def _get_manifest_files():
    filelist = FileList()
    old_wd = os.getcwd()
    try:
        os.chdir(SOURCE_DIRECTORY)
        filelist.findall()
    finally:
        os.chdir(old_wd)
    with open(MANIFEST, "r", encoding="utf-8") as source:
        for line in source:
            filelist.process_template_line(line.strip())
    filelist.process_template_line("prune .tox")
    return filelist.files


def trim_docstring(text):
    """
    Trim indentation and blank lines from docstring text & return it.

    See PEP 257.
    """
    if not text:
        return text
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = text.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxint
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxint:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return "\n".join(trimmed)


ALLOWED_SCHEMES = """file ftp gopher hdl http https imap mailto mms news nntp
prospero rsync rtsp rtspu sftp shttp sip sips snews svn svn+ssh telnet
wais""".split()


def render_readme_like_pypi(source, output_encoding="unicode"):
    """
    Render a ReST document just like PyPI does.
    """
    # Dedent all lines of `source`.
    source = trim_docstring(source)

    settings_overrides = {
        "raw_enabled": 0,  # no raw HTML code
        "file_insertion_enabled": 0,  # no file/URL access
        "halt_level": 2,  # at warnings or errors, raise an exception
        "report_level": 5,  # never report problems with the reST code
    }

    parts = None

    # Convert reStructuredText to HTML using Docutils.
    document = publish_doctree(source=source, settings_overrides=settings_overrides)

    for node in document.traverse():
        if node.tagname == "#text":
            continue
        if node.hasattr("refuri"):
            uri = node["refuri"]
        elif node.hasattr("uri"):
            uri = node["uri"]
        else:
            continue
        o = urlparse(uri)
        if o.scheme not in ALLOWED_SCHEMES:
            raise TransformError("link scheme not allowed: {0}".format(uri))

    # now turn the transformed document into HTML
    reader = readers.doctree.Reader(parser_name="null")
    pub = Publisher(
        reader, source=io.DocTreeInput(document), destination_class=io.StringOutput
    )
    pub.set_writer("html")
    pub.process_programmatic_settings(None, settings_overrides, None)
    pub.set_destination(None, None)
    pub.publish()
    parts = pub.writer.parts

    output = parts["body"]

    if output_encoding != "unicode":
        output = output.encode(output_encoding)

    return output


def test_manifest_complete():
    required_files = sorted(_get_required_files())
    included_files = sorted(_get_manifest_files())
    assert required_files == included_files


@pytest.mark.skipif(str("sys.version_info[0] > 2"))
def test_description_rendering():
    with open(README, "r", encoding="utf-8") as source:
        output = render_readme_like_pypi(source.read())
    assert output
