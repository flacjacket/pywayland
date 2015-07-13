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
from .eventloop import EventLoop


class Display(object):
    """Create a Wayland Display object"""
    def __init__(self, ptr=None):
        if ptr:
            self._ptr = ptr
        else:
            self._ptr = lib.wl_display_create()

    def __del__(self):
        self.destroy()

    def destroy(self):
        """Destroy Wayland display object.

        This function emits the :class:`Display` destroy signal, releases all
        the sockets added to this display, free's all the globals associated
        with this display, free's memory of additional shared memory formats
        and destroy the display object.

        .. seealso::

            :meth:`Display.add_destroy_listener()`
        """

        if self._ptr:
            lib.wl_display_destroy(self._ptr)
            self._ptr = None

    def add_socket(self, name=None):
        """Add a socket to Wayland display for the clients to connect.

        This adds a Unix socket to Wayland display which can be used by clients
        to connect to Wayland display.

        If `None` is passed as name, then it would look for `WAYLAND_DISPLAY`
        environment variable for the socket name. If `WAYLAND_DISPLAY` is not
        set, then default `wayland-0` is used.

        The Unix socket will be created in the directory pointed to by
        environment variable `XDG_RUNTIME_DIR`. If `XDG_RUNTIME_DIR` is not
        set, then this function throws an exception.

        The length of socket path, i.e., the path set in `XDG_RUNTIME_DIR` and
        the socket name, must not exceed the maxium length of a Unix socket
        path.  The function also fails if the user do not have write permission
        in the `XDG_RUNTIME_DIR` path or if the socket name is already in use.

        :param name: Name of the Unix socket.
        :type name: string or None
        """
        if name is None:
            name_ptr = lib.wl_display_add_socket_auto(self._ptr)
            name = ffi.string(name_ptr)

            if not name:
                # TODO: raise better
                raise Exception()

            return name
        else:
            name_ptr = ffi.new('char []', name.encode())
            ret = lib.wl_display_add_socket(self._ptr, name_ptr)

            if ret == -1:
                # TODO: raise better
                raise Exception()

    def get_serial(self):
        """Get the current serial number

        This function returns the most recent serial number, but does not
        increment it.
        """
        return lib.wl_display_get_serial(self._ptr)

    def next_serial(self):
        """Get the next serial

        This function increments the display serial number and returns the new
        value.
        """
        return lib.wl_display_next_serial(self._ptr)

    def get_event_loop(self):
        """Get the event loop for the display

        :returns: The :class:`~pywayland.server.EventLoop` for the Display
        """
        return EventLoop(self)

    def terminate(self):
        """Stop the display from running"""
        if self._ptr:
            lib.wl_display_terminate(self._ptr)

    def run(self):
        """Run the display"""
        lib.wl_display_run(self._ptr)
