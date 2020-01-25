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

import traceback
from typing import Callable, List, Optional, Union

from pywayland.protocol_core.message import Message
from pywayland import ffi, lib

CallbackT = Callable[..., Optional[int]]


# int (*wl_dispatcher_func_t)(const void *, void *, uint32_t, const struct wl_message *, union wl_argument *)
@ffi.def_extern()
def dispatcher_func(data, target, opcode, message, c_args):
    # `data` is the handle to proxy/resource python object
    # `target` is the wl_proxy/wl_resource for self, this should be the same as self._ptr
    # `message` is the wl_message for self._interface.events/requests[opcode]
    # TODO: handle any user_data attached to the wl_proxy/wl_resource

    # get the proxy/resource object from the user data handle
    self = ffi.from_handle(data)

    # get the callback
    func = self.dispatcher[opcode]
    if func is None:
        return 0

    # rebuild the args into python objects
    args = self.dispatcher.messages[opcode].c_to_arguments(c_args)

    try:
        ret = func(self, *args)
    except Exception:
        traceback.print_exc()
        return 0

    if ret is None:
        return 0
    else:
        return ret


# void (*wl_resource_destroy_func_t)(struct wl_resource *resource)
@ffi.def_extern()
def resource_destroy_func(res_ptr):
    # the user data to the resource is the handle to the resource
    resource_handle = lib.wl_resource_get_user_data(res_ptr)
    resource = ffi.from_handle(resource_handle)

    # if the destructor has been set, run it
    func = resource.dispatcher.destructor
    if func is not None:
        func(resource)


class Dispatcher:
    """Dispatches events or requests from an interface

    Handles the dispatching of callbacks from events (for
    :class:`~pywayland.sever.resource.Resource` objects) and requests (for
    :class:`~pywayland.client.proxy.Proxy` objects).  The callbacks for a given
    message can be set and retrieved by indexing the dispatcher with either the
    opcode or the name of the message.

    :param messages:
        List of messages (events or requests)
    :type messages:
        `list`
    :param destructor:
        Create destructor dispatcher (for Resources)
    :type destructor:
        `bool`
    """

    def __init__(self, messages: List[Message], destructor: bool = False) -> None:
        self.messages = messages

        # Create a map of message names to message opcodes
        self._names = {msg.name: opcode for opcode, msg in enumerate(messages)}
        self._callback: List[Optional[CallbackT]] = [None] * len(messages)

        if destructor:
            self.destructor = None

    def __getitem__(self, opcode_or_name: Union[str, int]) -> Optional[CallbackT]:
        if isinstance(opcode_or_name, str):
            opcode_or_name = self._names[opcode_or_name]

        return self._callback[opcode_or_name]

    def __setitem__(self, opcode_or_name: Union[str, int], function: CallbackT) -> None:
        if isinstance(opcode_or_name, str):
            opcode_or_name = self._names[opcode_or_name]
        self._callback[opcode_or_name] = function
