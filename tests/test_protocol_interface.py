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

from pywayland.protocol.wayland.buffer import Buffer
from pywayland.protocol.wayland.callback import Callback
from pywayland.protocol.wayland.compositor import Compositor
from pywayland.protocol.wayland.datadevicemanager import DataDeviceManager
from pywayland.protocol.wayland.datadevice import DataDevice
from pywayland.protocol.wayland.dataoffer import DataOffer
from pywayland.protocol.wayland.datasource import DataSource
from pywayland.protocol.wayland.display import Display
from pywayland.protocol.wayland.keyboard import Keyboard
from pywayland.protocol.wayland.output import Output
from pywayland.protocol.wayland.pointer import Pointer
from pywayland.protocol.wayland.region import Region
from pywayland.protocol.wayland.registry import Registry
from pywayland.protocol.wayland.seat import Seat
from pywayland.protocol.wayland.shell import Shell
from pywayland.protocol.wayland.shellsurface import ShellSurface
from pywayland.protocol.wayland.shmpool import ShmPool
from pywayland.protocol.wayland.shm import Shm
from pywayland.protocol.wayland.subcompositor import Subcompositor
from pywayland.protocol.wayland.subsurface import Subsurface
from pywayland.protocol.wayland.surface import Surface
from pywayland.protocol.wayland.touch import Touch

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
    (Buffer, C.wl_buffer_interface),
    (Callback, C.wl_callback_interface),
    (Compositor, C.wl_compositor_interface),
    (DataDeviceManager, C.wl_data_device_manager_interface),
    (DataDevice, C.wl_data_device_interface),
    (DataOffer, C.wl_data_offer_interface),
    (DataSource, C.wl_data_source_interface),
    (Display, C.wl_display_interface),
    (Keyboard, C.wl_keyboard_interface),
    (Output, C.wl_output_interface),
    (Pointer, C.wl_pointer_interface),
    (Region, C.wl_region_interface),
    (Registry, C.wl_registry_interface),
    (Seat, C.wl_seat_interface),
    (Shell, C.wl_shell_interface),
    (ShellSurface, C.wl_shell_surface_interface),
    (ShmPool, C.wl_shm_pool_interface),
    (Shm, C.wl_shm_interface),
    (Subcompositor, C.wl_subcompositor_interface),
    (Subsurface, C.wl_subsurface_interface),
    (Surface, C.wl_surface_interface),
    (Touch, C.wl_touch_interface),
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
            assert py_type == ffi.NULL
        else:
            assert py_type != ffi.NULL
            assert ffi.string(wl_type.name) == ffi.string(py_type.name)


def verify_wl_interface(py_cls, wl_ptr):
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


def test_display():
    for wl_cls, py_ptr in interfaces:
        yield verify_wl_interface, wl_cls, py_ptr
