#include <stdio.h>
#include <libudev.h>

int main() {
    int res;
    struct udev * context;
    struct udev_enumerate * enumerator;
    struct udev_device * device;
    struct udev_list_entry * entry;
    struct udev_list_entry * other_entry;
    struct udev_list_entry * start;
    char const * name;
    char const * value;
    context = udev_new();

    device = udev_device_new_from_syspath(
       context,
       "/sys/devices/LNXSYSTM:00/LNXSYBUS:00/PNP0A08:00/device:26/device:27"
    );

    printf("udev_list_entry_get_value()\n");
    printf("Correct behavior, values are not obtained.\n");
    entry = udev_device_get_sysattr_list_entry(device);
    while (entry) {
        name = udev_list_entry_get_name(entry);
        value = udev_list_entry_get_value(entry);
        printf("%s: %s\n", name, value);
        entry = udev_list_entry_get_next(entry);
    }
    printf("\n");

    printf("udev_device_get_sysattr_value()\n");
    printf("Incorrect behavior; physical_node should have a value.\n");
    entry = udev_device_get_sysattr_list_entry(device);
    while (entry) {
        name = udev_list_entry_get_name(entry);
        value = udev_device_get_sysattr_value(device, name);
        printf("%s: %s\n", name, value);
        entry = udev_list_entry_get_next(entry);
    }
    printf("\n");

    printf("udev_device_get_sysattr_value(bogus)\n");
    printf("correct behavior, value of non-existant attribute is null.\n");
    value = udev_device_get_sysattr_value(device, "bogus");
    printf("bogus: %s\n", value);
    printf("\n");

    printf("Should be like the first.\n");
    entry = udev_device_get_sysattr_list_entry(device);
    start = entry;
    while (entry) {
        name = udev_list_entry_get_name(entry);
        other_entry = udev_list_entry_get_by_name(start, name);
        value = udev_list_entry_get_value(other_entry);
        printf("%s: %s\n", name, value);
        entry = udev_list_entry_get_next(entry);
    }
    printf("\n");

    return 0;
}
