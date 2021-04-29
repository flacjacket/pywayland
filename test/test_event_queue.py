# Copyright 2021 Sean Vig
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

import time
import threading

import pytest

from pywayland.client.display import Display
from pywayland.client.eventqueue import EventQueue
from pywayland.server.display import Display as ServerDisplay


def _run_server():
    s = ServerDisplay()

    e = s.get_event_loop()
    source = e.add_timer(_kill_server, data=s)
    source.timer_update(500)

    s.add_socket()
    s.run()
    s.destroy()


def _kill_server(data):
    data.terminate()
    return 1


def test_event_queue():
    server = threading.Thread(target=_run_server)
    server.start()

    try:
        display = Display()
        start = time.time()
        while time.time() < start + 1:
            try:
                display.connect()
            except Exception:
                time.sleep(0.1)
            else:
                break
        else:
            pytest.fail("Could not connect to server")

        with display:
            event_queue = EventQueue(display)
            display.dispatch(queue=event_queue)
    finally:
        server.join()
