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

from __future__ import absolute_import, print_function

# import collections
import mmap
import os
import sys
import tempfile

this_file = os.path.abspath(__file__)
this_dir = os.path.split(this_file)[0]
root_dir = os.path.split(this_dir)[0]
pywayland_dir = os.path.join(root_dir, "pywayland")
if os.path.exists(pywayland_dir):
    sys.path.append(root_dir)

from pywayland.client import Display  # noqa: E402
from pywayland.protocol.wayland import (  # noqa: E402
    WlCompositor,
    WlSeat,
    WlShell,
    WlShm,
)


def create_shm_buffer(touch, width, height):
    stride = width * 4
    size = stride * height

    with tempfile.TemporaryFile() as f:
        f.write(b"\x64" * size)
        f.flush()

        fd = f.fileno()
        touch["data"] = mmap.mmap(
            fd, size, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE
        )
        pool = touch["shm"].create_pool(fd, size)
        touch["buffer"] = pool.create_buffer(
            0, width, height, stride, WlShm.format.argb8888.value
        )
        pool.destroy()


def handle_touch_down(wl_touch, serial, time, surface, id, x, y):
    # touch = wl_touch.user_data
    # touch_paint(touch, x, y, id)
    return 0


def handle_touch_motion(wl_touch, time, id, x, y):
    # touch = wl_touch.user_data
    # touch_paint(touch, x, y, id)
    return 0


def handle_seat_capabilities(wl_seat, capabilities):
    print("capabilities")
    seat = wl_seat.user_data
    touch = seat["touch"]

    if (capabilities & WlSeat.capability.touch.value) and seat["wl_touch"] is None:
        seat["wl_touch"] = wl_seat.get_touch()
        seat["wl_touch"].user_data = touch
        seat["wl_touch"].dispatcher["down"] = handle_touch_down
        # seat['wl_touch'].dispatcher['up'] = handle_touch_up
        seat["wl_touch"].dispatcher["motion"] = handle_touch_motion
    elif not (capabilities & WlSeat.capability.touch.value) and seat["wl_touch"]:
        seat["wl_touch"].destroy()
        seat["wl_touch"] = None
    return 1


def handle_shm_format(wl_shm, fmt):
    print("format")
    touch = wl_shm.user_data

    if fmt == WlShm.format.argb8888.value:
        touch["has_argb"] = True
    return 1


def handle_shell_surface_ping(wl_shell_surface, serial):
    print("ping")
    wl_shell_surface.pong(serial)
    return 1


def handle_registry_global(wl_registry, id_num, iface_name, version):
    print("global", id_num, iface_name)

    touch = wl_registry.user_data
    if iface_name == "wl_compositor":
        touch["compositor"] = wl_registry.bind(id_num, WlCompositor, version)
    elif iface_name == "wl_seat":
        seat = {}
        seat["touch"] = touch
        seat["wl_touch"] = None

        wl_seat = wl_registry.bind(id_num, WlSeat, version)
        wl_seat.dispatcher["capabilities"] = handle_seat_capabilities
        wl_seat.user_data = seat
        seat["seat"] = wl_seat
    elif iface_name == "wl_shell":
        touch["shell"] = wl_registry.bind(id_num, WlShell, version)
    elif iface_name == "wl_shm":
        touch["has_argb"] = False

        shm = wl_registry.bind(id_num, WlShm, version)
        shm.user_data = touch
        shm.dispatcher["format"] = handle_shm_format
        touch["shm"] = shm
    return 1


def touch_create(width, height):
    touch = {}

    # Make the display and get the registry
    touch["display"] = Display()
    touch["display"].connect()

    touch["registry"] = touch["display"].get_registry()
    touch["registry"].user_data = touch
    touch["registry"].dispatcher["global"] = handle_registry_global

    touch["display"].dispatch()
    touch["display"].roundtrip()
    touch["display"].roundtrip()

    if not touch["has_argb"]:
        print("WL_SHM_FORMAT_ARGB32 not available", file=sys.stderr)
        touch["display"].disconnect()
        return

    touch["width"] = width
    touch["height"] = height
    touch["surface"] = touch["compositor"].create_surface()
    touch["shell_surface"] = touch["shell"].get_shell_surface(touch["surface"])
    create_shm_buffer(touch, width, height)

    if touch["shell_surface"]:
        print("shell")
        touch["shell_surface"].dispatcher["ping"] = handle_shell_surface_ping
        touch["shell_surface"].set_toplevel()

    touch["surface"].user_data = touch
    touch["shell_surface"].set_title("simple-touch")

    touch["surface"].attach(touch["buffer"], 0, 0)
    touch["surface"].damage(0, 0, width, height)
    touch["surface"].commit()

    return touch


def main():
    touch = touch_create(600, 500)

    while touch["display"].dispatch() != -1:
        pass

    touch["display"].disconnect()


if __name__ == "__main__":
    main()
