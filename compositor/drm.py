from pywayland.protocol.wayland.shm import Shm

from .launcher import logger
from ._ffi_drm import ffi, lib

import os

DRM_MAJOR = 226


def is_drm_master(fd):
    magic = ffi.new("drm_magic_t *")
    return lib.drmGetMagic(fd, magic) == 0 and lib.drmAuthMagic(fd, magic[0]) == 0


def find_gpu(self):
    return "/dev/dri/card0"
    # There is a udev way to do this automatically...
    # c = pyudev.Context()
    # enumerator = pyudev.Enumerator(c)
    # enumerator.match_subsystem("drm")
    # enumerator.match_sys_name("card[0-9]*")

    # drm_device = None
    # for device in enumerator:
    #     return device.syspath


def fd_open(path, flags):
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    fd = os.open(path, flags)

    stat = os.fstat(fd)

    if os.major(stat.st_rdev) == DRM_MAJOR:
        logger.info("drm: got DRM_MAJOR")
        if not is_drm_master(fd):
            logger.exception("drm: fd not master")
            os.close(fd)
            raise OSError()
        return fd
    logger.exception("drm: fd not drm major")
    raise OSError()


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
        logger.info("drm: created gbm device")
        if gbm == ffi.NULL:
            raise Exception()
        self.gbm = gbm

        visual_id = ffi.new("EGLint []", [
            Shm.format.xrgb8888.value,
            Shm.format.argb8888.value,
            0
        ])

        if gl_renderer_supports("gbm"):
            get_platform_display = lib.eglGetProcAddress("eglGetPlatformDisplayExt")

    def destroy(self):
        logger.info("drm: destroying gbm device")
        self.gbm.destroy()
        lib.gbm_device_destroy(self.gbm)


class Drm(object):
    def __init__(self):
        path = find_gpu()
        logger.info("drm: opening %s", path)
        self.fd = fd_open(path, os.O_RDWR)

        self.gbm = None
        self.event_source = None

    def __enter__(self):
        self.create_buffer()

        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.destroy()

    def destroy(self):
        if self.event_source:
            self.event_source.remove()

        if self.gbm:
            self.gbm.destroy()
            self.gbm = None

        if self.fd is not None:
            os.close(self.fd)

    def create_buffer(self):
        self.gbm = Gbm(self.fd)

    def create_callback(self, eventloop):
        self.event_source = eventloop.add_fd(self.fd, self.drm_event)

    def drm_event(self, fd, mask, data):
        context = ffi.new("drmEventContext")
