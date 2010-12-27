#!/usr/bin/env python
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


"""
    library_path_wrapper
    ====================

    Set ``$LD_LIBRARY_PATH`` to the library directory of the current virtual
    environment and execute the given script with the given arguments.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""


import sys
import os



def update_library_path():
    lib_paths = os.environ.get('LD_LIBRARY_PATH', '').split(os.pathsep)
    environment_lib_directory = os.path.join(sys.prefix, 'lib')
    if environment_lib_directory not in lib_paths:
        # update the library to include the environments library and re-execute ourself
        lib_paths.insert(0, environment_lib_directory)
        lib_path = os.pathsep.join(lib_paths)
        os.environ['LD_LIBRARY_PATH'] = lib_path


def main():
    update_library_path()
    command = sys.argv[1:]
    os.execvp(command[0], command)


if __name__ == '__main__':
    main()

