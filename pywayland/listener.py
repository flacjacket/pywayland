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


@ffi.callback("int(void *, void *, uint32_t, struct wl_message *, union wl_argument *)")
def _dispatcher(data, target, opcode, message, c_args):
    # `data` is the handle to Proxy/Resource
    # `target` is the wl_proxy/wl_resource for self
    # `message` is the wl_message for self._interface.events/requests[opcode]
    # TODO: handle any user_data attached to the wl_proxy/wl_resource
    self = ffi.from_handle(data)
    args = self.listener.messages[opcode].c_to_arguments(c_args)

    func = self.listener[opcode]
    if func is None:
        return 0
    return func(self, *args)


@ffi.callback("void(struct wl_resource *)")
def _destroyed_dispatcher(res_ptr):
    res_py_ptr = C.wl_resource_get_user_data(res_ptr)

    if res_py_ptr == ffi.NULL:
        return

    res = ffi.from_handle(res_py_ptr)

    func = res.destructor
    if func is not None:
        func(res)


class Listener(object):
    def __init__(self, messages, destructor=False):
        self._names = {msg.name: opcode for opcode, msg in enumerate(messages)}
        self._func = [None for _ in messages]
        self.messages = messages
        self.dispatcher = _dispatcher
        if destructor:
            self.destroyed_dispatcher = _destroyed_dispatcher

    def __getitem__(self, opcode_or_name):
        if opcode_or_name in self._names:
            opcode_or_name = self._names[opcode_or_name]

        return self._func[opcode_or_name]

    def __setitem__(self, opcode_or_name, function):
        if opcode_or_name in self._names:
            opcode_or_name = self._names[opcode_or_name]
        self._func[opcode_or_name] = function
