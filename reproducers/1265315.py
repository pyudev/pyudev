# pylint: disable=invalid-name

"""
Report to generate examples for bz#1265315.
"""

from __future__ import print_function

import os
import stat

import pyudev

def main():
    """
    Print all devices which have available attributes w/ no value.

    Print all instance of such attributes which are not symlinked directories.

    If any of the not symlinked directories set are readable by the owner
    (presumably root), print those.
    """
    context = pyudev.Context()
    for device in context.list_devices():
        attributes = device.attributes
        attrs = [a for a in attributes if not a in attributes]
        if attrs:
            print("%s: %s" % (device, ", ".join(attrs)))
            path = device.sys_path
            pairs = ((attr, os.path.join(path, attr)) for attr in attrs)
            expected = lambda f: os.path.islink(f) and os.path.isdir(f)
            surprises = [(a, f) for (a, f) in pairs if not expected(f)]
            if surprises:
                fmt_str = "SURPRISE (not symlinked directories): %s"
                print(fmt_str % ", ".join(a for (a, f) in surprises))

                readable = lambda f: os.stat(f).st_mode & stat.S_IRUSR
                readables = [(a, f) for (a, f) in surprises if readable(f)]

                if readables:
                    fmt_str = "a subset were readable: %s"
                    print(fmt_str % ", ".join(a for (a, f) in readables))

if __name__ == "__main__":
    main()
