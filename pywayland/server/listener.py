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

import functools
import weakref

weakkeydict = weakref.WeakKeyDictionary()


def _wrap_listener_callback(f):
    @ffi.callback("void(struct wl_listener *listener, void *data)")
    @functools.wraps(f)
    def _listener_callback(listener_ptr, data_ptr):
        # TODO: figure out how to pass things in
        f()

    return _listener_callback


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
        self._ptr = ffi.new("struct wl_listener *")
        self.notify = function
        self.link = None

        self._ptr.notify = callback_ffi = _wrap_listener_callback(function)

        weakkeydict[self] = callback_ffi

    def remove(self):
        """Remove the listener"""
        if self.link:
            C.wl_list_remove(ffi.addressof(self._ptr.link))
            self.link = None
