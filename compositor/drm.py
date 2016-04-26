from .log_utils import logger
from ._ffi_compositor import ffi, lib

import os


def is_drm_master(fd):
    magic = ffi.new("drm_magic_t *")
    return lib.drmGetMagic(fd, magic) == 0 and lib.drmAuthMagic(fd, magic[0]) == 0


def find_gpu():
    return "/dev/dri/card0"
    # There is a udev way to do this automatically...
    # c = pyudev.Context()
    # enumerator = pyudev.Enumerator(c)
    # enumerator.match_subsystem("drm")
    # enumerator.match_sys_name("card[0-9]*")

    # drm_device = None
    # for device in enumerator:
    #     return device.syspath


def gl_renderer_supports(suffix):
    ext_ptr = lib.eglQueryString(ffi.NULL, lib.EGL_EXTENSIONS)
    extensions = ffi.string(ext_ptr).decode()
    logger.info("drm: got support for %s", extensions)

    if "EGL_EXT_platform_base" not in extensions:
        raise Exception()

    return any(
        "EGL_{}_platform_{}".format(prot, suffix) in extensions for prot in ("KHR", "EXT", "MESA")
    )


@ffi.def_extern()
def page_flip_handler_func(fd, sequence, tv_sec, tv_usec, user_data):
    logger.info("drm: got page flip")


class Drm(object):
    """Create a DRM backend tied to the given eventloop"""
    def __init__(self, ipc, eventloop):
        path = find_gpu()
        logger.info("drm: opening %s", path)

        flags = os.O_RDWR
        if hasattr(os, "O_CLOEXEC"):
            flags |= os.O_CLOEXEC
        self.fd = ipc.send_open_device(path, flags)

        self.gbm = lib.gbm_create_device(self.fd)

        if eventloop:
            self.event_source = eventloop.add_fd(self.fd, self.drm_event)
        else:
            self.event_source = None

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.destroy()

    def destroy(self):
        if self.event_source:
            self.event_source.remove()
            self.event_source = None

        lib.gbm_device_destroy(self.gbm)

    def drm_event(self, fd, mask, data):
        """Handle a DRM event"""
        # create the DRM event context, linking to the page flip handler
        context = ffi.new("drmEventContext*")
        context.version = lib.DRM_EVENT_CONTEXT_VERSION
        context.page_flip_handler = lib.page_flip_handler_func

        # handle the events using this context
        lib.drmHandleEvent(fd, context)

        return 0
