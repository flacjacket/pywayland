from pywayland.protocol.wayland.shm import Shm

from .log_utils import logger
from ._ffi_drm import ffi, lib

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


class Gbm(object):
    def __init__(self, fd):
        gbm = lib.gbm_create_device(fd)
        logger.info("gbm: created gbm device")
        if gbm == ffi.NULL:
            raise Exception()
        self.gbm = gbm

        #visual_id = ffi.new("EGLint []", [
        #    Shm.format.xrgb8888.value,
        #    Shm.format.argb8888.value,
        #    0
        #])

        #if gl_renderer_supports("gbm"):
        #    get_platform_display = lib.eglGetProcAddress("eglGetPlatformDisplayExt")

    def destroy(self):
        logger.info("gbm: destroying gbm device")
        lib.gbm_device_destroy(self.gbm)


@ffi.def_extern()
def page_flip_handler_func(fd, sequence, tv_sec, tv_usec, user_data):
    logger.info("drm: got page flip")


class Drm(object):
    def __init__(self, ipc, eventloop=None):
        path = find_gpu()
        logger.info("drm: opening %s", path)

        flags = os.O_RDWR
        if hasattr(os, "O_CLOEXEC"):
            flags |= os.O_CLOEXEC
        self.fd = ipc.send_open_device(path, flags)

        if eventloop:
            self.event_source = eventloop.add_fd(self.fd, self.drm_event)
        else:
            self.event_source = None

        self.gbm = None

    def __enter__(self):
        self.create_buffer()

        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.destroy()

    def destroy(self):
        if self.event_source:
            self.event_source.remove()
            self.event_source = None

        if self.gbm:
            self.gbm.destroy()
            self.gbm = None

    def create_buffer(self):
        self.gbm = Gbm(self.fd)

    def drm_event(self, fd, mask, data):
        context = ffi.new("drmEventContext*")
        context.version = lib.DRM_EVENT_CONTEXT_VERSION
        context.page_flip_handler = lib.page_flip_handler_func

        lib.drmHandleEvent(fd, context)
