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

from pywayland import ffi


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


class Listener(object):
    def __init__(self, messages):
        self._names = {msg.name: opcode for opcode, msg in enumerate(messages)}
        self._func = [None for _ in messages]
        self.messages = messages
        self.dispatcher = _dispatcher

    def __getitem__(self, opcode_or_name):
        if opcode_or_name in self._names:
            opcode_or_name = self._names[opcode_or_name]

        return self._func[opcode_or_name]

    def __setitem__(self, opcode_or_name, function):
        if opcode_or_name in self._names:
            opcode_or_name = self._names[opcode_or_name]
        if not isinstance(opcode_or_name, int):
            raise KeyError("Unable to set function for opcode {}".format(
                opcode_or_name)
            )
        if opcode_or_name >= len(self._func):
            raise KeyError("opcode too large, max opcode is {}, got {}".format(
                len(self._func) - 1, opcode_or_name
            ))
        self._func[opcode_or_name] = function
