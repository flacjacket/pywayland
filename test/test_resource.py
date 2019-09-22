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

from pywayland.server import Client, Listener, Display
from pywayland.protocol.wayland import WlDisplay

import socket


def test_create_resource():
    s1, s2 = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM, 0)
    display = Display()
    client = Client(display, s1.fileno())

    # Create resource
    res = WlDisplay.resource_class(client, version=4)

    assert res.version == 4

    # Fetching the client object by id gives the resource back again
    assert client.get_object(res.id) == res

    client.user_data = 0xbee
    assert client.user_data == 0xbee

    client.destroy()
    display.destroy()

    s2.close()


def _destroy_callback(data):
    global destroyed
    destroyed = True


def _destroy_notify(listener, data):
    global notified
    notified = True


def test_destroy_resource():
    global destroyed, notified
    destroyed = False
    notified = False

    s1, s2 = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM, 0)
    display = Display()
    client = Client(display, s1.fileno())
    listener = Listener(_destroy_notify)

    # Create resource
    res = WlDisplay.resource_class(client, version=4)
    # Attach a destructor and a destroy notification
    res.dispatcher.destructor = _destroy_callback
    res.add_destroy_listener(listener)
    # Destroy the resource
    res.destroy()

    assert destroyed
    assert notified

    assert client.get_object(res.id) is None

    # Create resource
    res = WlDisplay.resource_class(client, version=2)
    # Attach a destructor and a destroy notification
    res.dispatcher.destructor = _destroy_callback
    res.add_destroy_listener(listener)
    # Destroy the client
    client.destroy()

    assert destroyed
    assert notified

    display.destroy()

    s2.close()


def notest_create_resource_with_same_id():
    s1, s2 = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM, 0)
    display = Display()
    client = Client(display, s1.fileno())

    # Create resource
    res = WlDisplay.resource_class(client, version=2)
    assert client.get_object(res.id) == res

    # This should replace the old one
    res2 = WlDisplay.resource_class(client, version=1, id=res.id)
    assert client.get_object(res.id) == res2

    res2.destroy()
    res.destroy()

    client.destroy()
    display.destroy()

    s2.close()
