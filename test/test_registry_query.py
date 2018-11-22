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

import threading
import time

got_compositor = None


def _get_registry_callback(proxy, id, iface_name, version):
    global got_compositor
    if iface_name == 'wl_compositor':
        got_compositor = proxy
    return 1


def _run_client():
    global got_compositor
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

    c.roundtrip()

    c.disconnect()


def _kill_server(data):
    # the `data` is the server Display
    data.terminate()


def test_get_registry():
    global got_compositor
    got_compositor = None

    # run the client in a thread
    client = threading.Thread(target=_run_client)
    client.start()

    # create the server
    s = ServerDisplay()

    # Add a compositor so we can query for it (and keep it alive)
    compositor = WlCompositor.global_class(s)  # noqa

    # Add a timer to kill the server after 0.5 sec (should be more than enough
    # time, don't know a more deterministic way...)
    e = s.get_event_loop()
    source = e.add_timer(_kill_server, data=s)
    source.timer_update(500)

    # start up the server
    s.add_socket()
    s.run()
    s.destroy()

    # wait for the client (shouldn't block on roundtrip once the server is down)
    client.join()

    # make sure we got the compositor in the client
    assert got_compositor
