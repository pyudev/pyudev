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
    char const * attr;

    context = udev_new();
    // If the device with a subsystem is used, exit is 2.
    // If the device without a subsystem is used, exit is 0.

    // This device has a vpd_pg83 file with some binary contents.
    // But libudev does not report the contents.
    device = udev_device_new_from_syspath(context, "/sys/devices/pci0000:00/0000:00:03.0/0000:03:00.0/host1/target1:0:0/1:0:0:0");
    if (device == NULL) {
        return -1;
    }

    attr = udev_device_get_sysattr_value(device, "vpd_pg83");
    if (attr == NULL) {
        return -1; // no attribute file found
    }

    if (strlen(attr) > 0) {
        return -1; // suprise! this one has a non empty value this time
    }

    // This device seems just the same, i.e, it has a vpd_pg83 file with some binary contents.
    // But in this case, libudev reports a non-empty value.
    device = udev_device_new_from_syspath(context, "/sys/devices/pci0000:80/0000:80:02.0/0000:81:00.0/host2/target2:0:9/2:0:9:0");
    if (device == NULL) {
        return -1;
    }

    attr = udev_device_get_sysattr_value(device, "vpd_pg83");
    if (attr == NULL) {
        return -1; // no attribute file found
    }

    if (strlen(attr) == 0) {
        return -1; // suprise! this one has an empty value this time
    }

    // otherwise, returns 0
    return 0;
}
