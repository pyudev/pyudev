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
    Find a device which exists but which is not among devices listed.
    """
    context = pyudev.Context()
    device = pyudev.Device.from_name(context, 'block', 'sda1')
    no_subsys_dev = None
    for dev in device.ancestors:
        try:
            dev.subsystem
        except AttributeError:
            no_subsys_dev = dev
            break

    import pdb
    pdb.set_trace()
    devices = context.list_devices()

    if no_subsys_dev not in devices:
        return 0
    return 1

if __name__ == "__main__":
    main()
