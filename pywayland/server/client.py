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

import functools
import logging
from typing import Any, Optional, Tuple

from pywayland import ffi, lib
from pywayland.utils import ensure_valid
from .display import Display
from .listener import Listener


def _client_destroy(display: Display, cdata: "ffi.ClientCData") -> None:
    # do nothing if the display is already destroyed
    if display.destroyed:
        logging.error("Display destroyed before client")
        return

    lib.wl_client_destroy(cdata)


class Client:
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

    def __init__(self, display: Display, fd: int) -> None:
        if display.destroyed:
            raise ValueError("Display has been destroyed")

        ptr = lib.wl_client_create(display._ptr, fd)

        destructor = functools.partial(_client_destroy, display)
        self._ptr: Optional["ffi.ClientCData"] = ffi.gc(ptr, destructor)
        self._display: Optional[Display] = display

    def destroy(self) -> None:
        """Destroy the client"""
        if self._ptr is not None:
            ffi.release(self._ptr)
            self._ptr = None
            self._display = None

    @ensure_valid
    def flush(self) -> None:
        """Flush pending events to the client

        Events sent to clients are queued in a buffer and written to the socket
        later - typically when the compositor has handled all requests and goes
        back to block in the event loop.  This function flushes all queued up
        events for a client immediately.
        """
        assert self._ptr is not None
        lib.wl_client_flush(self._ptr)

    @ensure_valid
    def get_credentials(self) -> Tuple[int, int, int]:
        """Return Unix credentials for the client.

        This function returns the process ID, the user ID and the group ID for the given
        client. The credentials come from getsockopt() with SO_PEERCRED, on the client
        socket fd.
        """
        assert self._ptr is not None

        pid = ffi.new("pid_t *")
        uid = ffi.new("uid_t *")
        gid = ffi.new("gid_t *")
        lib.wl_client_get_credentials(self._ptr, pid, uid, gid)
        return pid[0], uid[0], gid[0]

    @ensure_valid
    def add_destroy_listener(self, listener: Listener) -> None:
        """Add a listener for the destroy signal

        :param listener: The listener object
        :type listener: :class:`~pywayland.server.Listener`
        """
        assert self._ptr is not None
        lib.wl_client_add_destroy_listener(self._ptr, listener._ptr)

    @ensure_valid
    def get_object(self, object_id: int) -> Any:
        """Look up an object in the client name space

        This looks up an object in the client object name space by its object
        ID.

        :param object_id: The object id
        :type object_id: `int`
        :returns:
            The object, or ``None`` if there is not object for the given ID
        """
        assert self._ptr is not None

        res_ptr = lib.wl_client_get_object(self._ptr, object_id)
        # If the object doesn't exist, this returns NULL, and asking for
        # forgiveness doesn't work, becuase it will seg fault
        if res_ptr == ffi.NULL:
            return None

        resource_handle = lib.wl_resource_get_user_data(res_ptr)
        return ffi.from_handle(resource_handle)
