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

from typing import Optional, TYPE_CHECKING

from pywayland import ffi, lib
from pywayland.utils import ensure_valid
from .eventloop import EventLoop

if TYPE_CHECKING:
    from typing_extensions import Literal


def _full_display_gc(ptr: "ffi.DisplayCData") -> None:
    """Destroy the Display cdata pointer, but only after destroying the clients"""
    lib.wl_display_destroy_clients(ptr)
    lib.wl_display_destroy(ptr)


class Display:
    """Create a Wayland Display object"""

    def __init__(self, ptr=None) -> None:
        if ptr is None:
            ptr = lib.wl_display_create()
            if ptr == ffi.NULL:
                raise MemoryError("Unable to create wl_display object")

        self._ptr = ffi.gc(ptr, _full_display_gc)

    def __enter__(self) -> "Display":
        """Use the Display in a context manager, which automatically destroys the Display"""
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> "Literal[False]":
        """Destroy the used display"""
        self.destroy()
        return False

    @property
    def destroyed(self) -> bool:
        """Returns if the display has been destroyed"""
        return self._ptr is None

    def destroy(self) -> None:
        """Destroy Wayland display object.

        This function emits the :class:`Display` destroy signal, releases all
        the sockets added to this display, free's all the globals associated
        with this display, free's memory of additional shared memory formats
        and destroy the display object.

        .. seealso::

            :meth:`Display.add_destroy_listener()`
        """
        if self._ptr is not None:
            ffi.release(self._ptr)
            self._ptr = None

    @ensure_valid
    def add_socket(self, name: Optional[str] = None) -> str:
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
            if name_ptr == ffi.NULL:
                raise RuntimeError("Unable to create socket")
            name = ffi.string(name_ptr)
        else:
            ret = lib.wl_display_add_socket(self._ptr, name.encode())

            if ret == -1:
                # TODO: raise better
                raise Exception()

        return name

    @ensure_valid
    def get_serial(self) -> int:
        """Get the current serial number

        This function returns the most recent serial number, but does not
        increment it.
        """
        return lib.wl_display_get_serial(self._ptr)

    @ensure_valid
    def next_serial(self) -> int:
        """Get the next serial

        This function increments the display serial number and returns the new
        value.
        """
        return lib.wl_display_next_serial(self._ptr)

    @ensure_valid
    def get_event_loop(self) -> EventLoop:
        """Get the event loop for the display

        :returns: The :class:`~pywayland.server.EventLoop` for the Display
        """
        return EventLoop(self)

    @ensure_valid
    def terminate(self) -> None:
        """Stop the display from running"""
        lib.wl_display_terminate(self._ptr)

    @ensure_valid
    def run(self) -> None:
        """Run the display"""
        lib.wl_display_run(self._ptr)

    @ensure_valid
    def init_shm(self) -> None:
        """Initialize shm for this display"""
        ret = lib.wl_display_init_shm(self._ptr)
        if ret == -1:
            raise MemoryError("Unable to create shm for display")

    @ensure_valid
    def add_shm_format(self, shm_format) -> None:
        """Add support for a Shm pixel format

        Add the specified :class:`~pywayland.protocol.wayland.WlShm.format`
        format to the list of formats the
        :class:`~pywayland.protocol.wayland.WlShm` object advertises when a
        client binds to it.  Adding a format to the list means that clients
        will know that the compositor supports this format and may use it for
        creating :class:`~pywayland.protocol.wayland.WlShm` buffers.  The
        compositor must be able to handle the pixel format when a client
        requests it.

        The compositor by default supports ``WL_SHM_FORMAT_ARGB8888`` and
        ``WL_SHM_FORMAT_XRGB8888``.

        :param shm_format: The shm pixel format to advertise
        :type shm_format: :class:`~pywayland.protocol.wayland.WlShm.format`
        """
        lib.wl_display_add_shm_format(self._ptr, shm_format.value)

    @ensure_valid
    def flush_clients(self) -> None:
        """Flush client connections"""
        lib.wl_display_flush_clients(self._ptr)
