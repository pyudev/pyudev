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

    // Uncomment below to get no match
    //res = udev_enumerate_add_nomatch_subsystem(enumerator, "i2c");
    //if (res < 0) {
    //    return res;
    //}

    // Uncomment below to get match
    //res = udev_enumerate_add_match_subsystem(enumerator, "i2c");
    //if (res < 0) {
    //    return res;
    //}

    // Leave both commented out to do no selection.

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
