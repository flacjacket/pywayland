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
from weakref import WeakKeyDictionary

from pywayland import ffi, lib

weakkeydict: WeakKeyDictionary = WeakKeyDictionary()


# void (*wl_global_bind_func_t)(struct wl_client *client, void *data, uint32_t version, uint32_t id)
@ffi.def_extern()
def global_bind_func(client_ptr, data, version, id) -> None:
    # `data` is the handle to Global
    callback_info = ffi.from_handle(data)

    version = min(callback_info["interface"].version, version)
    resource = callback_info["interface"].resource_class(client_ptr, version, id)

    # Call a user defined handler
    if callback_info["bind_func"]:
        # TODO: add some error catching so we don't segfault
        callback_info["bind_func"](resource)


def _global_destroy(display, cdata) -> None:
    if display._ptr is not None:
        # TODO: figure out how this can get run...
        # lib.wl_global_destroy(cdata)
        pass


class Global:
    """A server-side Interface object for the server

    Not created directly, created from the
    :class:`~pywayland.interface.Interface` object.

    :param display: The display the object is created on
    :type display: :class:`~pywayland.server.Display`
    :param version: The version to use for the
                    :class:`~pywayland.interface.Interface`, uses current
                    version if not specified
    :type version: `int`
    """

    def __init__(self, display, version=None):
        if display._ptr is None or display._ptr == ffi.NULL:
            raise ValueError("Display has been destroyed or couldn't initialize")

        if version is None:
            version = self.interface.version

        # we can't keep alive a handle to self without creating a reference
        # loop, so use this dict as the handle to pass to the global_bind_func
        # callback
        self._callback_info = {"interface": self.interface, "bind_func": None}
        self._handle = ffi.new_handle(self._callback_info)

        ptr = lib.wl_global_create(
            display._ptr,
            self.interface._ptr,
            version,
            self._handle,
            lib.global_bind_func,
        )
        destructor = functools.partial(_global_destroy, display)
        self._ptr = ffi.gc(ptr, destructor)
        self._display = display

        # this c data should keep the display alive
        weakkeydict[self._ptr] = display

    @property
    def bind_func(self):
        return self._callback_info["bind_func"]

    @bind_func.setter
    def bind_func(self, value):
        self._callback_info["bind_func"] = value

    def destroy(self):
        """Destroy the global object"""
        if self._ptr is not None:
            # run and remove destructor on c data
            _global_destroy(self._display, self._ptr)
            ffi.gc(self._ptr, None)
            self._ptr = None
            self._display = None
