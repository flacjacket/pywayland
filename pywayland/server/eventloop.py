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

from enum import Enum
import functools


# int (*wl_event_loop_fd_func_t)(int fd, uint32_t mask, void *data)
@ffi.def_extern()
def event_loop_fd_func(fd, mask, data_ptr):
    eventloop = ffi.from_handle(data_ptr)

    callback = eventloop.callbacks[data_ptr]
    data = eventloop.data[data_ptr]

    ret = callback(fd, mask, data)
    if isinstance(ret, int):
        return ret

    return 0


# int (*wl_event_loop_signal_func_t)(int signal_number, void *data)
@ffi.def_extern()
def event_loop_signal_func(signal_number, data_ptr):
    eventloop = ffi.from_handle(data_ptr)

    callback = eventloop.callbacks[data_ptr]
    data = eventloop.data[data_ptr]

    ret = callback(signal_number, data)
    if isinstance(ret, int):
        return ret

    return 0


# int (*wl_event_loop_timer_func_t)(void *data)
@ffi.def_extern()
def event_loop_timer_func(data_ptr):
    eventloop = ffi.from_handle(data_ptr)

    callback = eventloop.callbacks[data_ptr]
    data = eventloop.data[data_ptr]

    ret = callback(data)
    if isinstance(ret, int):
        return ret

    return 0


class EventLoop(object):
    """An event loop to add events too

    Returns an event loop.  Either returns the event loop of a given display
    (which will trigger when the Display is run), or creates a new event loop
    (which can be triggered by using :meth:`EventLoop.dispatch()`).

    :param display: The display to create the EventLoop on (default to `None`)
    :type display: :class:`~pywayland.server.Display`
    """

    fd_mask = Enum('fd_mask', {
        'WL_EVENT_READABLE': lib.WL_EVENT_READABLE,
        'WL_EVENT_WRITABLE': lib.WL_EVENT_WRITABLE,
        'WL_EVENT_HANGUP': lib.WL_EVENT_HANGUP,
        'WL_EVENT_ERROR': lib.WL_EVENT_ERROR
    })

    def __init__(self, display=None):
        if display:
            self._ptr = lib.wl_display_get_event_loop(display._ptr)
        else:
            self._ptr = lib.wl_event_loop_create()

        self.event_sources = []
        self.data = {}
        self.callbacks = {}

    def destroy(self):
        """Destroy the event loop"""
        # TODO: figure out when this should be run, definitely not always...
        if self._ptr:
            lib.wl_event_loop_destroy(self._ptr)
            self._ptr = None

    def add_fd(self, fd, callback, mask=[fd_mask.WL_EVENT_READABLE], data=None):
        """Add file descriptor callback

        Triggers function call when file descriptor state matches the mask.

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
        handle = ffi.new_handle(self)
        self.data[handle] = data
        self.callbacks[handle] = callback

        mask = [m.value for m in mask]
        mask = functools.reduce(lambda x, y: x | y, mask)

        event_source_cdata = lib.wl_event_loop_add_fd(self._ptr, fd, mask, lib.event_loop_fd_func, handle)
        event_source = EventSource(event_source_cdata)
        self.event_sources.append(event_source)

        return event_source

    def add_signal(self, signal_number, callback, data=None):
        """Add signal callback

        Triggers function call signal is received.

        :param signal_number: Signal number to trigger on
        :type signal_number: `int`
        :param callback: Callback function
        :type fd: function with callback `int(int signal_number, void *data)`
        :param data: User data to send to callback
        :type data: `object`
        :returns: :class:`EventSource` for specified callback
        """
        handle = ffi.new_handle(self)
        self.data[handle] = data
        self.callbacks[handle] = callback

        event_source_cdata = lib.wl_event_loop_add_signal(self._ptr, signal_number, lib.event_loop_signal_func, handle)
        event_source = EventSource(event_source_cdata)
        self.event_sources.append(event_source)

        return event_source

    def add_timer(self, callback, data=None):
        """Add timer callback

        Triggers function call after a specified time.

        :param callback: Callback function
        :type fd: function with callback `int(void *data)`
        :param data: User data to send to callback
        :type data: `object`

        .. seealso::

            :meth:`pywayland.server.eventloop.EventSource.timer_update()`
        """
        handle = ffi.new_handle(self)
        self.data[handle] = data
        self.callbacks[handle] = callback

        event_source_cdata = lib.wl_event_loop_add_timer(self._ptr, lib.event_loop_timer_func, handle)
        event_source = EventSource(event_source_cdata)
        self.event_sources.append(event_source)

        return event_source

    def add_destroy_listener(self, listener):
        """Add a listener for the destroy signal

        :params listener: The listener object
        :type listener: :class:`~pywayland.server.DestroyListener`
        """
        lib.wl_event_loop_add_destroy_listener(self._ptr, listener._ptr)
        listener.link = self

    def dispatch(self, timeout):
        """Dispatch callbacks on the event loop"""
        lib.wl_event_loop_dispatch(self._ptr, timeout)

    def dispatch_idle(self):
        """Dispatch idle callback on the event loop"""
        lib.wl_event_loop_dispatch_idle(self._ptr)


class EventSource(object):
    """Parameters for the EventLoop callbacks

    :param cdata: The struct corresponding to the EventSource
    :type cdata: `ffi cdata`
    """
    def __init__(self, cdata):
        self._ptr = cdata

    def remove(self):
        """Remove the callback from the event loop"""
        if self._ptr:
            lib.wl_event_source_remove(self._ptr)
        self._ptr = None

    def check(self):
        """Insert the EventSource into the check list"""
        lib.wl_event_source_check(self._ptr)

    def timer_update(self, timeout):
        """Set the timeout of the times callback

        :params timeout: Delay for timeout in ms
        :type timeout: `int`
        """
        lib.wl_event_source_timer_update(self._ptr, timeout)
