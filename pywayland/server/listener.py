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


# void (*wl_notify_func_t)(struct wl_listener *listener, void *data);
@ffi.def_extern()
def notify_func(listener_ptr, data):
    container = ffi.cast(
        "struct wl_listener_container *",
        ffi.cast("char*", listener_ptr) - ffi.offsetof("struct wl_listener_container", "destroy_listener")
    )
    listener = ffi.from_handle(container.handle)

    listener.notify(listener.link)


class DestroyListener(object):
    """A single listener for Wayland signals

    Provides the means to listen for `wl_listener` signal notifications.  Many
    Wayland objects use `wl_listener` for notification of significant events
    like object destruction.

    Clients should create :class:`DestroyListener` objects manually and can
    register them as listeners to objects using the object's
    ``.add_destroy_listener()`` method.  A listener can only listen to one
    signal at a time.
    """
    def __init__(self, function):
        self._handle = ffi.new_handle(self)
        # we need a way to get this Python object from the `struct
        # wl_listener*`, so we put the pointer in a container struct that
        # contains both the wl_listener and a pointer to our ffi handle
        self.container = ffi.new("struct wl_listener_container *")
        self.container.handle = self._handle

        self._ptr = ffi.addressof(self.container.destroy_listener)
        self._ptr.notify = lib.notify_func

        self.notify = function
        self.link = None

    def remove(self):
        """Remove the listener"""
        if self.link:
            lib.wl_list_remove(ffi.addressof(self._ptr.link))
            self.link = None
