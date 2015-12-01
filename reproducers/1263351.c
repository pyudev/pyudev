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

    /* correct, uses the actual name of the device, always works */
    device = udev_device_new_from_subsystem_sysname(
       context,
       "block",
       "sdaj"
    );
    if (device == NULL) {
        return 3;
    }

    /* sort of correct, uses the name with the subsystem prefix stripped,
      but works in that case.
    */
    device = udev_device_new_from_subsystem_sysname(
       context,
       "input",
       "event0" /* fails on name as reported by udevadm, "input/event0" */
    );
    if (device == NULL) {
        return 2;
    }

    /* fails no matter what, probably because name reported by mdadm does not
       contain a prefix identical to the subsystem string. */
    device = udev_device_new_from_subsystem_sysname(
       context,
       "iLO",
       "hpilo/d0ccb10"
    );
    if (device == NULL) {
        return 1;
    }

    return 0;
}
