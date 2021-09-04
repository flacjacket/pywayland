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

import enum
from weakref import WeakSet
from collections import namedtuple
from typing import List, Optional, TYPE_CHECKING

from pywayland import ffi, lib
from pywayland.utils import ensure_valid

if TYPE_CHECKING:
    from pywayland.server import Display  # noqa: F401

CallbackInfo = namedtuple("CallbackInfo", ["callback", "data"])

# TODO: add error handling to all callbacks


# int (*wl_event_loop_fd_func_t)(int fd, uint32_t mask, void *data)
@ffi.def_extern()
def event_loop_fd_func(fd, mask, data_ptr) -> int:
    callback_info = ffi.from_handle(data_ptr)

    ret = callback_info.callback(fd, mask, callback_info.data)
    if isinstance(ret, int):
        return ret

    return 0


# int (*wl_event_loop_signal_func_t)(int signal_number, void *data)
@ffi.def_extern()
def event_loop_signal_func(signal_number, data_ptr) -> int:
    callback_info = ffi.from_handle(data_ptr)

    ret = callback_info.callback(signal_number, callback_info.data)
    if isinstance(ret, int):
        return ret

    return 0


# int (*wl_event_loop_timer_func_t)(void *data)
@ffi.def_extern()
def event_loop_timer_func(data_ptr):
    callback_info = ffi.from_handle(data_ptr)

    ret = callback_info.callback(callback_info.data)
    if isinstance(ret, int):
        return ret

    return 0


# void (void *data)
@ffi.def_extern()
def event_loop_idle_func(data_ptr):
    callback_info = ffi.from_handle(data_ptr)

    callback_info.callback(callback_info.data)


class EventSource:
    """Parameters for the EventLoop callbacks

    :param cdata: The struct corresponding to the EventSource
    :type cdata: `ffi cdata`
    """

    def __init__(self, eventloop, cdata):
        self._eventloop = eventloop
        self._ptr = cdata

    def remove(self):
        """Remove the callback from the event loop"""
        if self._ptr is not None:
            lib.wl_event_source_remove(self._ptr)
        self._ptr = None

    @ensure_valid
    def check(self):
        """Insert the EventSource into the check list"""
        lib.wl_event_source_check(self._ptr)

    @ensure_valid
    def timer_update(self, timeout):
        """Set the timeout of the times callback

        :param timeout: Delay for timeout in ms
        :type timeout: `int`
        """
        lib.wl_event_source_timer_update(self._ptr, timeout)


class EventLoop:
    """An event loop to add events to

    Returns an event loop.  Either returns the event loop of a given display
    (which will trigger when the Display is run), or creates a new event loop
    (which can be triggered by using :meth:`EventLoop.dispatch()`).

    :param display: The display to create the EventLoop on (default to `None`)
    :type display: :class:`~pywayland.server.Display`
    """

    class FdMask(enum.IntFlag):
        WL_EVENT_READABLE = lib.WL_EVENT_READABLE
        WL_EVENT_WRITABLE = lib.WL_EVENT_WRITABLE
        WL_EVENT_HANGUP = lib.WL_EVENT_HANGUP
        WL_EVENT_ERROR = lib.WL_EVENT_ERROR

    def __init__(self, display: Optional["Display"] = None) -> None:
        if display:
            self._ptr: Optional["ffi.EventLoopCData"] = lib.wl_display_get_event_loop(
                display._ptr
            )
        else:
            # if we are creating an eventloop. we need to destroy it later
            ptr = lib.wl_event_loop_create()
            self._ptr = ffi.gc(ptr, lib.wl_event_loop_destroy)

        self.event_sources: WeakSet[EventSource] = WeakSet()
        self._callback_handles: List = []

    def destroy(self):
        """Destroy the event loop"""
        if self._ptr is not None:
            for event_source in self.event_sources:
                event_source.remove()
            # destroy the pointer and remove the destructor
            ffi.release(self._ptr)
            self._ptr = None

    @ensure_valid
    def add_fd(self, fd, callback, mask=FdMask.WL_EVENT_READABLE, data=None):
        """Add file descriptor callback

        Triggers function call when file descriptor state matches the mask.

        The callback should take three arguments:

            * `fd` - file descriptor (int)
            * `mask` - file descriptor mask (uint)
            * `data` - any object

        :param fd: File descriptor
        :type fd: `int`
        :param callback: Callback function
        :type fd: function with callback `int(int fd, uint32_t mask, void
                  *data)`
        :param mask: File descriptor mask
        :type fd: `int`
        :param data: User data to send to callback
        :type data: `object`
        :returns: :class:`EventSource` for specified callback

        .. seealso::

            :meth:`pywayland.server.eventloop.EventSource.check()`
        """
        callback = CallbackInfo(callback=callback, data=data)
        handle = ffi.new_handle(callback)
        self._callback_handles.append(handle)

        event_source_cdata = lib.wl_event_loop_add_fd(
            self._ptr, fd, mask.value, lib.event_loop_fd_func, handle
        )
        event_source = EventSource(self, event_source_cdata)
        self.event_sources.add(event_source)

        return event_source

    @ensure_valid
    def add_signal(self, signal_number, callback, data=None):
        """Add signal callback

        Triggers function call signal is received.

        The callback should take three arguments:

            * `signal_number` - signal (int)
            * `data` - any object

        :param signal_number: Signal number to trigger on
        :type signal_number: `int`
        :param callback: Callback function
        :type fd: function with callback `int(int signal_number, void *data)`
        :param data: User data to send to callback
        :type data: `object`
        :returns: :class:`EventSource` for specified callback
        """
        callback = CallbackInfo(callback=callback, data=data)
        handle = ffi.new_handle(callback)
        self._callback_handles.append(handle)

        event_source_cdata = lib.wl_event_loop_add_signal(
            self._ptr, signal_number, lib.event_loop_signal_func, handle
        )
        event_source = EventSource(self, event_source_cdata)
        self.event_sources.add(event_source)

        return event_source

    @ensure_valid
    def add_timer(self, callback, data=None):
        """Add timer callback

        Triggers function call after a specified time.

        The callback should take one argument:

            * `data` - any object

        :param callback: Callback function
        :type callback: function with callback `int(void *data)`
        :param data: User data to send to callback
        :type data: `object`
        :returns: :class:`EventSource` for specified callback

        .. seealso::

            :meth:`pywayland.server.eventloop.EventSource.timer_update()`
        """
        callback = CallbackInfo(callback=callback, data=data)
        handle = ffi.new_handle(callback)
        self._callback_handles.append(handle)

        event_source_cdata = lib.wl_event_loop_add_timer(
            self._ptr, lib.event_loop_timer_func, handle
        )
        event_source = EventSource(self, event_source_cdata)
        self.event_sources.add(event_source)

        return event_source

    @ensure_valid
    def add_idle(self, callback, data=None):
        """Add idle callback

        :param callback: Callback function
        :type callback: function with callback `void(void *data)`
        :param data: User data to send to callback
        :returns: :class:`EventSource` for specified callback
        """
        callback = CallbackInfo(callback=callback, data=data)
        handle = ffi.new_handle(callback)
        self._callback_handles.append(handle)

        event_source_cdata = lib.wl_event_loop_add_idle(
            self._ptr, lib.event_loop_idle_func, handle
        )
        event_source = EventSource(self, event_source_cdata)
        self.event_sources.add(event_source)

        return event_source

    @ensure_valid
    def add_destroy_listener(self, listener):
        """Add a listener for the destroy signal

        :param listener: The listener object
        :type listener: :class:`~pywayland.server.Listener`
        """
        lib.wl_event_loop_add_destroy_listener(self._ptr, listener._ptr)

    @ensure_valid
    def dispatch(self, timeout):
        """Dispatch callbacks on the event loop"""
        lib.wl_event_loop_dispatch(self._ptr, timeout)

    @ensure_valid
    def dispatch_idle(self):
        """Dispatch idle callback on the event loop"""
        lib.wl_event_loop_dispatch_idle(self._ptr)
