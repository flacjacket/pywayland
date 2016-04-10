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

import re
import weakref

weakkeydict = weakref.WeakKeyDictionary()

re_args = re.compile(r'(\??)([fsoanuih])')


class Proxy(object):
    """Represents a protocol object on the client side.

    A :class:`Proxy` acts as a client side proxy to an object existing in the
    compositor.  Events coming from the compositor are also handled by the
    proxy, which will in turn call the handler set with
    :func:`Proxy.add_listener`.
    """
    def __init__(self, ptr):
        self._ptr = ptr

        self.user_data = None

        # This should only be true for wl_display proxies, as they will
        # initialize its pointer on a `.connect()` call
        if self._ptr is None:
            return

        self._handle = ffi.new_handle(self)

        _ptr = ffi.cast('struct wl_proxy *', self._ptr)
        lib.wl_proxy_add_dispatcher(_ptr, lib.dispatcher_func, self._handle, ffi.NULL)

    def __del__(self):
        self._destroy()

    def _destroy(self):
        """Frees the pointer associated with the Proxy"""
        if self._ptr:
            # TODO: figure out how to destroy the proxy in the right order
            # _ptr = ffi.cast('struct wl_proxy *', self._ptr)
            # lib.wl_proxy_destroy(_ptr)
            self._ptr = None

    def _marshal(self, opcode, *args):
        """Marshal the given arguments into the Wayland wire format"""
        # Create a wl_argument array
        args_ptr = self._interface.requests[opcode].arguments_to_c(*args)
        # Make the cast to a wl_proxy
        proxy = ffi.cast('struct wl_proxy *', self._ptr)

        lib.wl_proxy_marshal_array(proxy, opcode, args_ptr)

    def _marshal_constructor(self, opcode, interface, *args):
        """Marshal the given arguments into the Wayland wire format for a constructor"""
        # Create a wl_argument array
        args_ptr = self._interface.requests[opcode].arguments_to_c(*args)
        # Make the cast to a wl_proxy
        proxy = ffi.cast('struct wl_proxy *', self._ptr)

        proxy_ptr = lib.wl_proxy_marshal_array_constructor(
            proxy, opcode, args_ptr, interface._ptr
        )
        return interface.proxy_class(proxy_ptr)
