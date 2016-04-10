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


# int (*wl_dispatcher_func_t)(const void *, void *, uint32_t, const struct wl_message *, union wl_argument *)
@ffi.def_extern()
def dispatcher_func(data, target, opcode, message, c_args):
    # `data` is the handle to Proxy/Resource
    # `target` is the wl_proxy/wl_resource for self
    # `message` is the wl_message for self._interface.events/requests[opcode]
    # TODO: handle any user_data attached to the wl_proxy/wl_resource

    # So this is _massively_ broken, but somehow resources give NULL data, but
    # the user data is not null
    if data == ffi.NULL:
        data = lib.wl_resource_get_user_data(target)

    self = ffi.from_handle(data)
    args = self.dispatcher.messages[opcode].c_to_arguments(c_args)

    func = self.dispatcher[opcode]
    if func is not None:
        ret = func(self, *args)
    else:
        ret = 0

    if ret is None:
        return 0
    else:
        return ret


# void (*wl_resource_destroy_func_t)(struct wl_resource *resource)
@ffi.def_extern()
def resource_destroy_func(res_ptr):
    res_py_ptr = lib.wl_resource_get_user_data(res_ptr)

    if res_py_ptr == ffi.NULL:
        return

    res = ffi.from_handle(res_py_ptr)

    func = res.destructor
    if func is not None:
        func(res)


class Dispatcher(object):
    """Dispatches events or requests from an interface

    Handles the dispatching of callbacks from events (for
    :class:`~pywayland.sever.resource.Resource` objects) and requests (for
    :class:`~pywayland.client.proxy.Proxy` objects).  The callbacks for a given
    message can be set and retrieved by indexing the dispatcher with either the
    opcode or the name of the message.

    :param messages: List of messages (events or requests)
    :type messages: `list`
    :param destructor: Create destructor dispatcher (for Resources)
    :type destructor: `bool`
    """
    def __init__(self, messages, destructor=False):
        self.messages = messages

        # Create a map of message names to message opcodes
        self._names = {msg.name: opcode for opcode, msg in enumerate(messages)}
        self._callback = [None] * len(messages)

    def __getitem__(self, opcode_or_name):
        if opcode_or_name in self._names:
            opcode_or_name = self._names[opcode_or_name]

        return self._callback[opcode_or_name]

    def __setitem__(self, opcode_or_name, function):
        if opcode_or_name in self._names:
            opcode_or_name = self._names[opcode_or_name]
        self._callback[opcode_or_name] = function
