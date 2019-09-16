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

from pywayland.client import Display as ClientDisplay
from pywayland.server import Display as ServerDisplay

from pywayland.protocol.wayland import WlCompositor

import time
import threading


def _get_registry_callback(registry, id, iface_name, version):
    global compositor
    if iface_name == 'wl_compositor':
        compositor = registry.bind(id, WlCompositor, version)


def _run_client():
    c = ClientDisplay()
    start = time.time()
    while time.time() < start + 10:
        try:
            c.connect()
        except Exception:
            time.sleep(0.1)
            continue
        break

    reg = c.get_registry()
    reg.dispatcher['global'] = _get_registry_callback

    c.dispatch(block=True)
    c.roundtrip()

    c.disconnect()


def _bind_handler(registry):
    global bound
    bound = registry


def _kill_server(data):
    # the `data` is the server Display
    data.terminate()
    return 1


def test_get_registry():
    global bound, compositor
    bound = None
    compositor = None

    # run the client in a thread
    client = threading.Thread(target=_run_client)
    client.start()

    # create a server
    s = ServerDisplay()

    # Add a compositor so we can query for it
    global_ = WlCompositor.global_class(s)
    global_.bind_func = _bind_handler

    # Add a timer to kill the server after 0.5 sec (should be more than enough
    # time, don't know a more deterministic way...)
    e = s.get_event_loop()
    source = e.add_timer(_kill_server, data=s)
    source.timer_update(500)

    # start the server
    s.add_socket()
    s.run()
    s.destroy()

    # wait for the client (shouldn't block on roundtrip once the server is down)
    client.join()

    # make sure we got the compositor in the client
    assert compositor
    # and that it has the compositor requests
    assert compositor.create_surface

    # Check that the server got the bind and ran the handler
    assert bound is not None
