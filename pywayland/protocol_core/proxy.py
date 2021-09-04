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

from typing import Type, TYPE_CHECKING

from pywayland import ffi, lib
from pywayland.dispatcher import Dispatcher
from pywayland.utils import ensure_valid

if TYPE_CHECKING:
    from .interface import Interface  # noqa: F401


class Proxy:
    interface: Type["Interface"]

    def __init__(self, ptr, display=None):
        """Represents a protocol object on the client side.

        A :class:`Proxy` acts as a client side proxy to an object existing in
        the compositor.  Events coming from the compositor are also handled by
        the proxy, which will in turn call the handler set with
        :func:`Proxy.add_listener`.
        """
        self.user_data = None
        self.dispatcher = Dispatcher(self.interface.events)

        # This should only be true for wl_display proxies, as they will
        # initialize its pointer on a `.connect()` call
        if ptr is None:
            self._ptr = ptr
            self._display = self
            return

        self._display = display

        # parent display is the root-most client Display object, all proxies
        # should keep the display alive
        if display is None:
            raise ValueError(
                "Non-Display Proxy objects must be associated to a Display"
            )
        display._children.add(self)

        if ptr == ffi.NULL:
            raise RuntimeError("Got a null pointer for the proxy")

        # note that even though we cast to a proxy here, the ptr may be a
        # wl_display, so the methods must still cast to 'struct wl_proxy *'
        ptr = ffi.cast("struct wl_proxy *", ptr)
        self._ptr = ffi.gc(ptr, lib.wl_proxy_destroy)

        self._handle = ffi.new_handle(self)
        lib.wl_proxy_add_dispatcher(
            self._ptr, lib.dispatcher_func, self._handle, ffi.NULL
        )

        self.interface.registry[self._ptr] = self

    @property
    def destroyed(self) -> bool:
        """Determine if proxy has been destroyed

        Returns true if the proxy has been destroyed.
        """
        return self._ptr is None

    def __del__(self) -> None:
        self._destroy()

    def _destroy(self) -> None:
        """Frees the pointer associated with the Proxy"""
        if self._ptr is not None:
            if self._display._ptr is not None:
                ffi.release(self._ptr)
            else:
                self._ptr = ffi.gc(self._ptr, None)
            self._ptr = None

    destroy = _destroy

    @ensure_valid
    def _marshal(self, opcode, *args):
        """Marshal the given arguments into the Wayland wire format"""
        # Create a wl_argument array
        args_ptr = self.interface.requests[opcode].arguments_to_c(*args)

        # Write the event into the connection queue
        proxy = ffi.cast("struct wl_proxy *", self._ptr)
        lib.wl_proxy_marshal_array(proxy, opcode, args_ptr)

    @ensure_valid
    def _marshal_constructor(self, opcode, interface, *args):
        """Marshal the given arguments into the Wayland wire format for a constructor"""
        # Create a wl_argument array
        args_ptr = self.interface.requests[opcode].arguments_to_c(*args)

        # Write the event into the connection queue and build a new proxy from the given args
        proxy = ffi.cast("struct wl_proxy *", self._ptr)
        proxy_ptr = lib.wl_proxy_marshal_array_constructor(
            proxy, opcode, args_ptr, interface._ptr
        )

        return interface.proxy_class(proxy_ptr, self._display)
