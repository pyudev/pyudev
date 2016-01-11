#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <libudev.h>

int main() {
    int res;
    struct udev * context;
    struct udev_device * device;
    struct udev_enumerate * enumerator;
    struct udev_list_entry * entry;
    char const * name;
    char const * dev_name;

    context = udev_new();
    // If the device with a subsystem is used, exit is 2.
    // If the device without a subsystem is used, exit is 0.

    // This device has a subsystem. It is a very standard block device.
    device = udev_device_new_from_syspath(context, "/sys/devices/pci0000:00/0000:00:1f.2/ata1/host0/target0:0:0/0:0:0:0/block/sda");
    // This device has no subsystem. It is an ancestor of above device.
    device = udev_device_new_from_syspath(context, "/sys/devices/pci0000:00/0000:00:1f.2/ata1");
    if (device == NULL) {
        return -1;
    }

    // The device has a perfectly valid syspath.
    dev_name = udev_device_get_syspath(device);
    if (dev_name == NULL) {
        return -1;
    }

    enumerator = udev_enumerate_new(context);
    res = udev_enumerate_scan_devices(enumerator);
    if (res < 0) {
        return res;
    }

    // returns 2 if the device is among the list of devices
    entry = udev_enumerate_get_list_entry(enumerator);
    while (entry) {
        name = udev_list_entry_get_name(entry);
        if (strcmp(dev_name, name) == 0) {
            return 2;
        }
        entry = udev_list_entry_get_next(entry);
    }

    // otherwise, returns 0
    return 0;
}
