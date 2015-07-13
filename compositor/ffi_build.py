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

ffi_launch.set_source('compositor._ffi_launcher', """
#include <linux/kd.h>
#include <linux/major.h>
#include <linux/vt.h>
""")

ffi_launch.cdef("""
#define TTY_MAJOR ...

#define KDGKBMODE ...
#define KDSKBMODE ...
#define KDSETMODE ...
#define KDGETMODE ...

#define K_OFF ...
#define KD_GRAPHICS ...

#define VT_SETMODE ...
#define VT_AUTO ...
#define VT_PROCESS ...
#define VT_ACKACQ ...
#define VT_ACTIVATE ...

#define VT_RELDISP ...

struct vt_mode {
    char mode;          /* vt mode */
    char waitv;         /* if set, hang on writes if not active */
    short relsig;       /* signal to raise on release req */
    short acqsig;       /* signal to raise on acquisition */
    short frsig;        /* unused (set to 0) */
};
""")

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
int drmSetMaster(int fd);
int drmDropMaster(int fd);

typedef unsigned int drm_magic_t;
int drmGetMagic(int fd, drm_magic_t * magic);
int drmAuthMagic(int fd, drm_magic_t magic);

typedef struct _drmEventContext {
    int version;
    void (*vblank_handler) (int fd,
                            unsigned int sequence,
                            unsigned int tv_sec,
                            unsigned int tv_usec,
                            void *user_data)
    void (*page_flip_handler) (int fd,
                               unsigned int sequence,
                               unsigned int tv_sec,
                               unsigned int tv_usec,
                               void *user_data)
} drmEventContext;

// ---------------------------------------------------------
// libgbm
struct gbm_device;
struct gbm_device *gbm_create_device(int fd);
void gbm_device_destroy(struct gbm_device *gbm);

// ---------------------------------------------------------
// libEGL
typedef void* EGLDisplay;

typedef ... EGLNativeDisplayType;
typedef int32_t EGLint;

EGLDisplay eglGetDisplay(
EGLBoolean eglInitialize(EGLDiplay display, EGLint *major, EGLint *minor);
""")

if __name__ == "__main__":
    ffi_launch.compile()
    ffi_drm.compile()
