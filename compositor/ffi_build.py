from cffi import FFI
import itertools
import os
import subprocess


def get_includes(package):
    pkg_config_exe = os.environ.get('PKG_CONFIG', None) or 'pkg-config'
    cmd = '{} --cflags lib{}'.format(pkg_config_exe, package).split()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, _ = proc.communicate()

    out = out.rstrip().decode('utf-8')
    includes = [token[2:] for token in out.split() if token[:2] == "-I"]
    return includes


ffi_launch = FFI()
swc_defs = """
struct swc_launch_request {
    enum {
        SWC_LAUNCH_REQUEST_OPEN_DEVICE,
        SWC_LAUNCH_REQUEST_ACTIVATE_VT,
    } type;

    uint32_t serial;

    union {
        struct /* OPEN_DEVICE */
        {
            int flags;
            char path[0];
        };
        struct /* ACTIVATE_VT */
        {
            unsigned vt;
        };
    };
};

struct swc_launch_event {
    enum {
        SWC_LAUNCH_EVENT_RESPONSE,
        SWC_LAUNCH_EVENT_ACTIVATE,
        SWC_LAUNCH_EVENT_DEACTIVATE,
    } type;

    union {
        struct /* RESPONSE */
        {
            uint32_t serial;
            bool success;
        };
    };
};"""

ffi_launch.set_source("compositor._ffi_launch", "#include <stdbool.h>" + swc_defs)
ffi_launch.cdef(swc_defs)

ffi_drm = FFI()

libs = ["drm", "gbm", "EGL", "GLESv2"]
dirs = list(itertools.chain.from_iterable(map(get_includes, libs)))

ffi_drm.set_source("compositor._ffi_drm", """
#include <xf86drm.h>

#include <gbm.h>

#include <EGL/egl.h>
#include <EGL/eglext.h>
""", libraries=libs, include_dirs=dirs)


ffi_drm.cdef("""
// ---------------------------------------------------------
// libdrm
#define DRM_EVENT_CONTEXT_VERSION ...

typedef struct _drmEventContext {
    int version;
    void (*vblank_handler) (int fd,
                            unsigned int sequence,
                            unsigned int tv_sec,
                            unsigned int tv_usec,
                            void *user_data);
    void (*page_flip_handler) (int fd,
                               unsigned int sequence,
                               unsigned int tv_sec,
                               unsigned int tv_usec,
                               void *user_data);
} drmEventContext, *drmEventContextPtr;

typedef unsigned int drm_magic_t;
int drmGetMagic(int fd, drm_magic_t * magic);
int drmAuthMagic(int fd, drm_magic_t magic);
int drmHandleEvent(int fd, drmEventContextPtr evctx);

// ---------------------------------------------------------
// libgbm
struct gbm_device;
struct gbm_device *gbm_create_device(int fd);
void gbm_device_destroy(struct gbm_device *gbm);

// ---------------------------------------------------------
// libEGL
typedef unsigned int EGLBoolean;
typedef void* EGLDisplay;

typedef ... EGLNativeDisplayType;
typedef int32_t EGLint;

char const * eglQueryString(EGLDisplay display, EGLint name);
void * eglGetProcAddress(const char *procname);
EGLBoolean eglInitialize(EGLDisplay display, EGLint *major, EGLint *minor);

// ---------------------------------------------------------
extern "Python" void page_flip_handler_func(int, unsigned int, unsigned int, unsigned int, void*);
""")

if __name__ == "__main__":
    ffi_launch.compile()
    ffi_drm.compile()
