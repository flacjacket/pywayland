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

from typing import Callable

from pywayland import ffi, lib
from pywayland.utils import wl_container_of


# void (*wl_notify_func_t)(struct wl_listener *listener, void *data);
@ffi.def_extern()
def notify_func(listener_ptr, data):
    container = wl_container_of(
        listener_ptr, "struct wl_listener_container *", "destroy_listener"
    )
    listener = ffi.from_handle(container.handle)

    if listener._signal is not None and listener._signal._data_wrapper is not None:
        data = listener._signal._data_wrapper(data)

    callback = listener._notify
    callback(listener, data)


class Listener:
    """A single listener for Wayland signals

    Provides the means to listen for `wl_listener` signal notifications.  Many
    Wayland objects use `wl_listener` for notification of significant events
    like object destruction.

    Clients should create :class:`Listener` objects manually and can register
    them as listeners to objects destroy events using the object's
    ``.add_destroy_listener()`` method.  A listener can only listen to one
    signal at a time.

    :param function: callback function for the Listener
    :type function: callable
    """

    container: "ffi.ListenerContainerCData"

    def __init__(self, function: Callable) -> None:
        self._handle = ffi.new_handle(self)

        # we need a way to get this Python object from the `struct
        # wl_listener*`, so we put the pointer in a container struct that
        # contains both the wl_listener and a pointer to our ffi handle
        self.container = ffi.new("struct wl_listener_container *")  # type: ignore[assignment]
        self.container.handle = self._handle

        self._ptr = ffi.addressof(self.container.destroy_listener)
        self._ptr.notify = lib.notify_func
        self._notify = function
        self._signal = None

    def remove(self) -> None:
        """Remove the listener"""
        if self._ptr.link != ffi.NULL:
            lib.wl_list_remove(ffi.addressof(self._ptr.link))
            self.link = None


class Signal:
    """A source of a type of observable event

    Signals are recognized points where significant events can be observed.
    Compositors as well as the server can provide signals. Observers are
    wl_listener's that are added through #wl_signal_add. Signals are emitted
    using #wl_signal_emit, which will invoke all listeners until that listener
    is removed by wl_list_remove() (or whenever the signal is destroyed).
    """

    def __init__(self, *, ptr=None, data_wrapper=None):
        if ptr is None:
            self._ptr = ffi.new("struct wl_listener *")
            lib.wl_signal_init(self._ptr)
        else:
            self._ptr = ptr

        self._data_wrapper = data_wrapper
        self._link = []

    def add(self, listener):
        """Add the specified listener to this signal

        :param listener: The listener to add
        :type listener: :class:`Listener`
        """
        # we are creating a reference loop, as the listener resolves the data
        # wrapper function, and the signal keeps the listener alive
        listener._signal = self
        self._link.append(listener)

        lib.wl_signal_add(self._ptr, listener._ptr)

    def emit(self, data=None):
        """Emits this signal, notifying all registered listeners

        :param data: The data that will be emitted with the signal
        """
        if data is not None:
            data_ptr = ffi.new_handle(data)
        else:
            data_ptr = ffi.NULL
        lib.wl_signal_emit(self._ptr, data_ptr)
