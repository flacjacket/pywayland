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
import weakref

weakkeydict = weakref.WeakKeyDictionary()


@ffi.def_extern()
def global_bind_func(client_ptr, data, version, id):
    # `data` is the handle to Global
    _global = ffi.from_handle(data)

    version = min(_global._interface.version, version)
    resource = _global._interface.resource_class(client_ptr, version, id)

    # Call a user defined handler
    if _global.bind_handler:
        _global.bind_handler(resource)


class Global(object):
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
            version = self._interface.version
        self.bind_handler = None

        def global_destroy(cdata):
            if display._ptr is None:
                return
            lib.wl_global_destroy(cdata)

        self._handle = ffi.new_handle(self)
        ptr = lib.wl_global_create(display._ptr, self._interface._ptr,
                                   version, self._handle, lib.global_bind_func)
        self._ptr = ffi.gc(ptr, global_destroy)

        # this object and its cdata should keep the display alive
        weakkeydict[self] = weakkeydict[self._ptr] = display

    def destroy(self):
        """Destroy the global object"""
        # let the garbage collector run wl_global_destroy
        self._ptr = None
