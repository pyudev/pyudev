#include <stdio.h>
#include <libudev.h>

int main() {
    int res;
    struct udev * context;
    struct udev_enumerate * enumerator;
    struct udev_device * device;
    struct udev_list_entry * entry;
    char const * name;
    char const * path;
    context = udev_new();
    enumerator = udev_enumerate_new(context);
    device = udev_device_new_from_syspath(context, "/sys/devices/LNXSYSTM:00/LNXSYBUS:00/PNP0A08:00");

    path = udev_device_get_sysattr_value(device, "path");
    printf("path before: %s\n", path);

    // Uncomment line below to get no match, will contain device
    // udev_enumerate_add_nomatch_sysattr(enumerator, "path", path);

    // Uncomment line below to get match, will be empty
    udev_enumerate_add_match_sysattr(enumerator, "path", path);

    printf("Printing devices...\n");
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

    path = udev_device_get_sysattr_value(device, "path");
    printf("path after: %s\n", path);

    return 0;
}
