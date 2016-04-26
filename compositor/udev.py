from ._ffi_compositor import ffi, lib


class Udev(object):
    def __init__(self, eventloop):
        self.udev = lib.udev_new()
        if self.udev == ffi.NULL:
            raise MemoryError("Unable to allocate udev handle")

        self.monitor = lib.udev_monitor_new_from_netlink(self.udev, "udev")
        if self.monitor == ffi.NULL:
            raise MemoryError("Unable to allocate udev monitor")

        udev_monitor_filter_add_match_subsystem_devtype(self.monitor, "drm", ffi.NULL)
        udev_monitor_filter_add_match_subsystem_devtype(self.monitor, "input", ffi.NULL)

        if udev_monitor_enable_receiving(self.monitor) < 0:
            pass

        self.event_source = None
        self.setup_event_loop(eventloop)

        # add activate_listener to activate signal

    def destroy(self):
        # remove listener

        # un-set eventloop

        if self.monitor:
            lib.udev_monitor_unref(self.monitor)
            self.monitor = None

        if self.udev:
            lib.udev_unref(self.udev)
            self.udev = None

    def setup_event_loop(self, eventloop):
        assert self.udev
        assert self.monitory

        if self.event_source:
            self.event_source.remove()

        fd = lib.udev_monitor_get_fd(self.monitor)
        self.event_source = eventloop.add_fd(fd, self.udev_event)  # to-do: add data

    def udev_event(self, fd, mask, data):
        pass
