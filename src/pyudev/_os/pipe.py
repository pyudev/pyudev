# -*- coding: utf-8 -*-
# Copyright (C) 2013 Sebastian Wiesner <lunaryorn@gmail.com>

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
    pyudev._os.pipe
    ===============

    Class wrapper for pipe.

    .. moduleauthor:: Sebastian Wiesner  <lunaryorn@gmail.com>
"""

# isort: FUTURE
from __future__ import annotations

# isort: STDLIB
import os


class Pipe:
    """A unix pipe.

    A pipe object provides two file objects: :attr:`source` is a readable file
    object, and :attr:`sink` a writeable.  Bytes written to :attr:`sink` appear
    at :attr:`source`.

    Open a pipe with :meth:`open()`.

    """

    @classmethod
    def open(cls) -> Pipe:
        """Open and return a new :class:`Pipe`.

        The pipe uses non-blocking IO."""
        source_fd, sink_fd = os.pipe2(os.O_NONBLOCK | os.O_CLOEXEC)
        return cls(source_fd, sink_fd)

    def __init__(self, source_fd: int, sink_fd: int):
        """Create a new pipe object from the given file descriptors.

        ``source_fd`` is a file descriptor for the readable side of the pipe,
        ``sink_fd`` is a file descriptor for the writeable side."""
        self.source = os.fdopen(source_fd, "rb", 0)
        self.sink = os.fdopen(sink_fd, "wb", 0)

    def close(self) -> None:
        """Closes both sides of the pipe."""
        try:
            self.source.close()
        finally:
            self.sink.close()
