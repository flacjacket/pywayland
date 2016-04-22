from pywayland.server import Display

from .compositor import Compositor
from .drm import Drm
from .swc_client import SwcClient

import os


def kill_server(server):
    server.terminate()


if __name__ == "__main__":
    fd = os.getenv("SWC_LAUNCH_SOCKET")
    fd = int(fd)

    ipc_client = SwcClient(fd)

    display = Display()

    sock = os.getenv("WAYLAND_DISPLAY", "wayland-0")
    display.add_socket(sock)
    # loop = display.get_event_loop()
    # TODO: hook up SIGTERM/SIGINT/SIGQUIT eventloop callbacks

    with Drm(ipc_client) as drm:
        c = Compositor(display)

        e = display.get_event_loop()
        s = e.add_timer(kill_server, display)
        s.timer_update(2000)
        display.run()
