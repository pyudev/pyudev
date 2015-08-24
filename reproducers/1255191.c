#include <stdio.h>
#include <libudev.h>

int main() {
    int res;
    struct udev * context;
    struct udev_enumerate * enumerator;
    struct udev_device * device;
    struct udev_list_entry * entry;
    char const * name;
    context = udev_new();
    enumerator = udev_enumerate_new(context);
    device = udev_device_new_from_syspath(context, "/sys/devices/system/memory");
    res = udev_enumerate_add_match_parent(enumerator, device);
    if (res < 0) {
        return res;
    }

    res = udev_enumerate_scan_devices(enumerator);
    if (res < 0) {
        return res;
    }

    entry = udev_enumerate_get_list_entry(enumerator);
    while (entry) {
        name = udev_list_entry_get_name(entry);
        printf("%s\n", name);
        entry = udev_list_entry_get_next(entry);
    }

    return 0;
}
