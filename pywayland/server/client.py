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

from pywayland import ffi, lib


class Client(object):
    """Create a client for the given file descriptor

    Given a file descriptor corresponding to one end of a socket, create a
    client struct and add the new client to the compositors client list.  At
    that point, the client is initialized and ready to run, as if the client
    had connected to the servers listening socket.

    The other end of the socket can be passed to
    :meth:`~pywayland.client.Display.connect()` on the client side or used with
    the WAYLAND_SOCKET environment variable on the client side.

    :param display: The display object
    :type display: :class:`Display`
    :param fd: The file descriptor for the socket to the client
    :type fd: `int`
    """
    def __init__(self, display, fd):
        if display._ptr == ffi.NULL:
            raise ValueError("Display pointer cannot be null")
        self._ptr = lib.wl_client_create(display._ptr, fd)

        self.display = display

    def __del__(self):
        self.destroy()

    def destroy(self):
        """Destroy the client"""
        if self._ptr:
            lib.wl_client_destroy(self._ptr)
        self._ptr = None

    def flush(self):
        """Flush pending events to the client

        Events sent to clients are queued in a buffer and written to the socket
        later - typically when the compositor has handled all requests and goes
        back to block in the event loop.  This function flushes all queued up
        events for a client immediately.
        """
        lib.wl_client_flush(self._ptr)

    def add_destroy_listener(self, listener):
        """Add a listener for the destroy signal

        :params listener: The listener object
        :type listener: :class:`~pywayland.server.DestroyListener`
        """
        lib.wl_client_add_destroy_listener(self._ptr, listener._ptr)
        listener.link = self

    def get_object(self, id):
        """Look up an object in the client name space

        This looks up an object in the client object name space by its object
        ID.

        :param id: The object id
        :type id: `int`
        :returns: The object, or ``None`` if there is not object for the given
                  ID
        """

        res_ptr = lib.wl_client_get_object(self._ptr, id)
        # If the object doesn't exist, this returns NULL, and asking for
        # forgiveness doesn't work, becuase it will seg fault
        if res_ptr == ffi.NULL:
            return
        res_py_ptr = lib.wl_resource_get_user_data(res_ptr)
        return ffi.from_handle(res_py_ptr)
