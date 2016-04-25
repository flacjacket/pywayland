from pywayland.server import Display

from .compositor import Compositor
from .drm import Drm
from .swc_client import SwcClient

import os


def kill_server(server):
    server.terminate()


if __name__ == "__main__":
    fd = int(os.getenv("SWC_LAUNCH_SOCKET"))

    ipc_client = SwcClient(fd)

    display = Display()

    display_sock = os.getenv("WAYLAND_DISPLAY", "wayland-0")
    display.add_socket(display_sock)
    os.setenv("WAYLAND_DISPLAY", display_sock)
    # loop = display.get_event_loop()
    # TODO: hook up SIGTERM/SIGINT/SIGQUIT eventloop callbacks

    # udev?

    # libinput?

    c = Compositor(display)

    e = display.get_event_loop()
    s = e.add_timer(kill_server, display)
    s.timer_update(2000)

    with Drm(ipc_client) as drm:
        display.run()
