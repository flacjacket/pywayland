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

from pywayland.server.client import Client
from pywayland.server.display import Display
from pywayland.server.listener import Listener

import socket


def destroy_notify_a(*args):
    global a
    a = 1


def destroy_notify_b(*args):
    global b
    b = 1


def test_client_destroy_listener():
    global a, b
    s1, s2 = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM, 0)
    a = 0
    b = 0

    display = Display()
    client = Client(display, s1.fileno())

    destroy_listener_a = Listener(destroy_notify_a)
    destroy_listener_b = Listener(destroy_notify_b)

    client.add_destroy_listener(destroy_listener_a)
    client.add_destroy_listener(destroy_listener_b)

    destroy_listener_a.remove()

    client.destroy()

    assert a == 0
    assert b == 1
