# Copyright 2015 Sean Vig
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from cffi import FFI
import re

import pytest

from pywayland.protocol.wayland import (
    WlBuffer,
    WlCallback,
    WlCompositor,
    WlDataDeviceManager,
    WlDataDevice,
    WlDataOffer,
    WlDataSource,
    WlDisplay,
    WlKeyboard,
    WlOutput,
    WlPointer,
    WlRegion,
    WlRegistry,
    WlSeat,
    WlShell,
    WlShellSurface,
    WlShmPool,
    WlShm,
    WlSubcompositor,
    WlSubsurface,
    WlSurface,
    WlTouch,
)

ffi = FFI()

ffi.cdef("""
struct wl_message {
    const char *name;
    const char *signature;
    const struct wl_interface **types;
};
struct wl_interface {
    const char *name;
    int version;
    int method_count;
    const struct wl_message *methods;
    int event_count;
    const struct wl_message *events;
};

extern const struct wl_interface wl_buffer_interface;
extern const struct wl_interface wl_callback_interface;
extern const struct wl_interface wl_compositor_interface;
extern const struct wl_interface wl_data_device_manager_interface;
extern const struct wl_interface wl_data_device_interface;
extern const struct wl_interface wl_data_offer_interface;
extern const struct wl_interface wl_data_source_interface;
extern const struct wl_interface wl_display_interface;
extern const struct wl_interface wl_keyboard_interface;
extern const struct wl_interface wl_output_interface;
extern const struct wl_interface wl_pointer_interface;
extern const struct wl_interface wl_region_interface;
extern const struct wl_interface wl_registry_interface;
extern const struct wl_interface wl_seat_interface;
extern const struct wl_interface wl_shell_interface;
extern const struct wl_interface wl_shell_surface_interface;
extern const struct wl_interface wl_shm_pool_interface;
extern const struct wl_interface wl_shm_interface;
extern const struct wl_interface wl_subcompositor_interface;
extern const struct wl_interface wl_subsurface_interface;
extern const struct wl_interface wl_surface_interface;
extern const struct wl_interface wl_touch_interface;
""")

C = ffi.verify("""
#include <wayland-server-protocol.h>
""", libraries=['wayland-server', 'wayland-client'])

# Check the generated cdata interfaces against actual ones, list of all
# interfaces as of wayland 1.7.0
interfaces = [
    (WlBuffer, C.wl_buffer_interface),
    (WlCallback, C.wl_callback_interface),
    (WlCompositor, C.wl_compositor_interface),
    (WlDataDeviceManager, C.wl_data_device_manager_interface),
    (WlDataDevice, C.wl_data_device_interface),
    (WlDataOffer, C.wl_data_offer_interface),
    (WlDataSource, C.wl_data_source_interface),
    (WlDisplay, C.wl_display_interface),
    (WlKeyboard, C.wl_keyboard_interface),
    (WlOutput, C.wl_output_interface),
    (WlPointer, C.wl_pointer_interface),
    (WlRegion, C.wl_region_interface),
    (WlRegistry, C.wl_registry_interface),
    (WlSeat, C.wl_seat_interface),
    (WlShell, C.wl_shell_interface),
    (WlShellSurface, C.wl_shell_surface_interface),
    (WlShmPool, C.wl_shm_pool_interface),
    (WlShm, C.wl_shm_interface),
    (WlSubcompositor, C.wl_subcompositor_interface),
    (WlSubsurface, C.wl_subsurface_interface),
    (WlSurface, C.wl_surface_interface),
    (WlTouch, C.wl_touch_interface),
]

re_arg = re.compile(r"(\??)([uifsonah])")


def verify_wl_message(py_ptr, wl_ptr):
    """Verify the wl_message

    Check the wl_message associated with the given cdata pointer against the
    given wl_interface object
    """
    assert ffi.string(wl_ptr.name) == ffi.string(py_ptr.name)
    assert ffi.string(wl_ptr.signature) == ffi.string(py_ptr.signature)

    signature = ffi.string(wl_ptr.signature).decode()
    nargs = len(re_arg.findall(signature))
    for j in range(nargs):
        wl_type = wl_ptr.types[j]
        py_type = py_ptr.types[j]
        if wl_type == ffi.NULL:
            assert py_type == ffi.NULL, j
        else:
            assert py_type != ffi.NULL
            assert ffi.string(wl_type.name) == ffi.string(py_type.name)


@pytest.mark.parametrize("py_cls,wl_ptr", interfaces)
def test_wl_interface(py_cls, wl_ptr):
    """ Verify that the wl_interface of the Python class

    Check the wl_interface associated with the given Python class against the
    given wl_interface object
    """
    py_ptr = py_cls._ptr

    assert ffi.string(wl_ptr.name) == ffi.string(py_ptr.name)
    assert wl_ptr.version == py_ptr.version
    assert wl_ptr.event_count == py_ptr.event_count

    assert wl_ptr.method_count == py_ptr.method_count
    for i in range(wl_ptr.method_count):
        verify_wl_message(py_ptr.methods[i], wl_ptr.methods[i])

    assert wl_ptr.event_count == py_ptr.event_count
    for i in range(wl_ptr.event_count):
        verify_wl_message(py_ptr.events[i], wl_ptr.events[i])
