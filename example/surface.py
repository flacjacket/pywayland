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

import mmap
import os
import sys

this_file = os.path.abspath(__file__)
this_dir = os.path.split(this_file)[0]
root_dir = os.path.split(this_dir)[0]
pywayland_dir = os.path.join(root_dir, "pywayland")
if os.path.exists(pywayland_dir):
    sys.path.append(root_dir)

from pywayland.client import Display  # noqa: E402
from pywayland.protocol.wayland import WlCompositor, WlShell, WlShm  # noqa: E402
from pywayland.utils import AnonymousFile  # noqa: E402

WIDTH = 480
HEIGHT = 256

MARGIN = 10


class Window(object):
    def __init__(self):
        self.buffer = None
        self.compositor = None
        self.shell = None
        self.shm = None
        self.shm_data = None
        self.surface = None

        self.line_pos = MARGIN
        self.line_speed = +1


def shell_surface_ping_handler(shell_surface, serial):
    shell_surface.pong(serial)
    print("pinged/ponged")


def shm_format_handler(shm, format_):
    if format_ == WlShm.format.argb8888.value:
        s = "ARGB8888"
    elif format_ == WlShm.format.xrgb8888.value:
        s = "XRGB8888"
    elif format_ == WlShm.format.rgb565.value:
        s = "RGB565"
    else:
        s = "other format"
    print("Possible shmem format: {}".format(s))


def registry_global_handler(registry, id_, interface, version):
    window = registry.user_data
    if interface == "wl_compositor":
        print("got compositor")
        window.compositor = registry.bind(id_, WlCompositor, version)
    elif interface == "wl_shell":
        print("got shell")
        window.shell = registry.bind(id_, WlShell, version)
    elif interface == "wl_shm":
        print("got shm")
        window.shm = registry.bind(id_, WlShm, version)
        window.shm.dispatcher["format"] = shm_format_handler


def registry_global_remover(registry, id_):
    print("got a registry losing event for {}".format(id))


def create_buffer(window):
    stride = WIDTH * 4
    size = stride * HEIGHT

    with AnonymousFile(size) as fd:
        window.shm_data = mmap.mmap(
            fd, size, prot=mmap.PROT_READ | mmap.PROT_WRITE, flags=mmap.MAP_SHARED
        )
        pool = window.shm.create_pool(fd, size)
        buff = pool.create_buffer(0, WIDTH, HEIGHT, stride, WlShm.format.argb8888.value)
        pool.destroy()
    return buff


def create_window(window):
    window.buffer = create_buffer(window)
    window.surface.attach(window.buffer, 0, 0)
    window.surface.commit()


def redraw(callback, time, destroy_callback=True):
    window = callback.user_data
    if destroy_callback:
        callback._destroy()

    paint(window)
    window.surface.damage(0, 0, WIDTH, HEIGHT)

    callback = window.surface.frame()
    callback.dispatcher["done"] = redraw
    callback.user_data = window

    window.surface.attach(window.buffer, 0, 0)
    window.surface.commit()


def paint(window):
    mm = window.shm_data
    # clear
    mm.seek(0)
    mm.write(b"\xff" * 4 * WIDTH * HEIGHT)

    # draw progressing line
    mm.seek((window.line_pos * WIDTH + MARGIN) * 4)
    mm.write(b"\x00\x00\x00\xff" * (WIDTH - 2 * MARGIN))
    window.line_pos += window.line_speed

    # maybe reverse direction of progression
    if window.line_pos >= HEIGHT - MARGIN or window.line_pos <= MARGIN:
        window.line_speed = -window.line_speed


def main():
    window = Window()

    display = Display()
    display.connect()
    print("connected to display")

    registry = display.get_registry()
    registry.dispatcher["global"] = registry_global_handler
    registry.dispatcher["global_remove"] = registry_global_remover
    registry.user_data = window

    display.dispatch(block=True)
    display.roundtrip()

    if window.compositor is None:
        raise RuntimeError("no compositor found")
    elif window.shell is None:
        raise RuntimeError("no shell found")
    elif window.shm is None:
        raise RuntimeError("no shm found")

    window.surface = window.compositor.create_surface()

    shell_surface = window.shell.get_shell_surface(window.surface)
    shell_surface.set_toplevel()
    shell_surface.dispatcher["ping"] = shell_surface_ping_handler

    frame_callback = window.surface.frame()
    frame_callback.dispatcher["done"] = redraw
    frame_callback.user_data = window

    create_window(window)
    redraw(frame_callback, 0, destroy_callback=False)

    while display.dispatch(block=True) != -1:
        pass

    import time

    time.sleep(1)

    display.disconnect()


if __name__ == "__main__":
    main()
