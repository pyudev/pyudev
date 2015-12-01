#include <stdio.h>
#include <libudev.h>

int main() {
    int res;
    struct udev * context;
    struct udev_enumerate * enumerator;
    struct udev_device * device;
    struct udev_device * new_device;
    struct udev_list_entry * entry;
    char const * sys_name;
    char const * subsystem;
    context = udev_new();

    device = udev_device_new_from_syspath(
       context,
       /* comment the line below and uncomment the one below that, it works. */
       "/sys/devices/pci0000:00/0000:00:1c.2/0000:01:00.2/iLO/hpilo!d0ccb0"
       /* "/sys/devices/LNXSYSTM:00/LNXPWRBN:00/input/input0/event0" */
    );
    if (device == NULL) {
        return 1;
    }

    sys_name = udev_device_get_sysname(device);
    if (sys_name == NULL) {
        return 2;
    }
    printf("%s\n", sys_name);

    subsystem = udev_device_get_subsystem(device);
    if (subsystem == NULL) {
        return 3;
    }
    printf("%s\n", subsystem);

    new_device = udev_device_new_from_subsystem_sysname(
       context,
       subsystem,
       sys_name
    );

    if (new_device == NULL) {
        return 4;
    }

    return 0;
}
