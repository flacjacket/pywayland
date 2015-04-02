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

from pywayland import ffi, C
import re

re_args = re.compile(r'(\??)([fsoanuih])')


@ffi.callback("int(void *, void *, uint32_t, struct wl_message *, union wl_argument *)")
def _dispatcher(data, target, opcode, message, c_args):
    # `data` is the handle to self
    # `target` is the wl_proxy for self
    # `message` is the wl_message for self._interface.events[opcode]
    # TODO: handle any user_data attached to the wl_proxy
    self = ffi.from_handle(data)
    args = self._interface.events[opcode].c_to_arguments(c_args)

    if opcode in self.listener:
        self.listener[opcode](self, *args)

    return 0


class Proxy(object):
    """Represents a protocol object on the client side.

    A :class:`Proxy` acts as a client side proxy to an object existing in the
    compositor.  Events coming from the compositor are also handled by the
    proxy, which will in turn call the handler set with
    :func:`Proxy.add_listener`.
    """
    def __init__(self):
        self.listener = {}
        self.user_data = None
        self._user_data = None

        self._handle = _handle = ffi.new_handle(self)

        # This should only be true for wl_display proxies, as they will
        # initialize its pointer on a `.connect()` call
        if self._ptr is None:
            return

        _ptr = ffi.cast('struct wl_proxy *', self._ptr)
        C.wl_proxy_add_dispatcher(_ptr, _dispatcher, _handle, ffi.NULL)

    def add_listener(self, callback, opcode=None, name=None):
        """Add listener for an event

        Add listener for an event, either by ``opcode`` (passed as an int) or
        by the name of the event, ``name`` (passed as a string).  Exactly one
        of these parameters must be set.
        """
        if (opcode and name) or not (opcode or name):
            raise ValueError("Exactly one of `opcode` or `name` can be set")

        if name:
            for opcode, event in self._interface.events.items():
                if event.name == name:
                    break
            else:
                raise ValueError("Could not find event with name {}".format(name))

        self.listener[opcode] = callback

    def get_listener(self):
        """Get the listeners for the interface events"""
        return self.listener

    def set_user_data(self, data):
        """Set the user data for the proxy"""
        self.user_data = data
        _ptr = ffi.cast('struct wl_proxy *', self._ptr)
        C.wl_proxy_set_user_data(_ptr, data)

    def get_user_data(self):
        """Get the user data for the proxy"""
        return self.user_data

    def _destroy(self):
        if self._ptr:
            _ptr = ffi.cast('struct wl_proxy *', self._ptr)
            C.wl_proxy_destroy(_ptr)
            self._ptr = None

    def _marshal(self, opcode, *args):
        # Create a wl_argument array
        args_ptr = self._interface.requests[opcode].arguments_to_c(*args)
        # Make the cast to a wl_proxy
        proxy = ffi.cast('struct wl_proxy *', self._ptr)

        C.wl_proxy_marshal_array(proxy, opcode, args_ptr)

    def _marshal_constructor(self, opcode, interface, *args):
        # Create a wl_argument array
        args_ptr = self._interface.requests[opcode].arguments_to_c(*args)
        # Make the cast to a wl_proxy
        proxy = ffi.cast('struct wl_proxy *', self._ptr)

        proxy_ptr = C.wl_proxy_marshal_array_constructor(
            proxy, opcode, args_ptr, interface._ptr
        )
        return interface.proxy_class(proxy_ptr)


class ProxyMeta(type):
    """Metaclass to initialize proxy classes from interfaces

    The base class must define an ``._interface`` parameter corresponding to an
    :class:`~pywayland.interface.Interface`, a ``._ptr`` parameter
    corresponding to the ``wl_proxy`` cdata pointer, and a ``.requests``
    parameter giving a list of :class:`~pywayland.message.Message`'s that will
    be added to the new :class:`Proxy` class to be returned.  The `_ptr` is
    cast to the correct type for the interface and the functions of each method
    are added to the class as methods.
    """
    def __new__(cls, name, bases, dct):
        assert '_interface' in dct
        assert '_ptr' in dct

        # We'll construct the proxy class from the interface
        interface = dct['_interface']

        # Cast the pointer to the right type
        dct['_ptr'] = ffi.cast('struct {} *'.format(interface.name), dct['_ptr'])

        # Get name from interface
        new_name = ''.join(x.capitalize() for x in interface.name.split('_')[1:])

        # Create new class
        new_class = type(new_name, (Proxy, ), dct)
        # Add requests out of interface to new class
        for msg in interface.requests:
            setattr(new_class, msg.name, msg._func)

        return new_class
