from pywayland.server import Display

from .compositor import Compositor
from .drm import Drm
from .launcher import Launcher

import os


def kill_server(server):
    server.terminate()


with Launcher() as t:
    display = Display()
    sock = os.getenv("WAYLAND_DISPLAY", "wayland-0")
    display.add_socket(sock)
    # loop = display.get_event_loop()
    # TODO: hook up SIGTERM/SIGINT/SIGQUIT eventloop callbacks

    with Drm() as drm:
        c = Compositor(display)

        e = display.get_event_loop()
        s = e.add_timer(kill_server, display)
        s.timer_update(2000)
        display.run()
