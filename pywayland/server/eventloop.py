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
import weakref

weakkeydict = weakref.WeakKeyDictionary()


def _wrap_fd_callback(f):
    @ffi.callback("int(int fd, uint32_t mask, void *data)")
    @functools.wraps(f)
    def _signal_callback(fd, mask, data_ptr):
        if data_ptr == ffi.NULL:
            data = None
        else:
            data = ffi.from_handle(data_ptr)

        return f(fd, mask, data)

    return _signal_callback


def _wrap_signal_callback(f):
    @ffi.callback("int(int signal_number, void *data)")
    @functools.wraps(f)
    def _signal_callback(signal_number, data_ptr):
        if data_ptr == ffi.NULL:
            data = None
        else:
            data = ffi.from_handle(data_ptr)

        return f(signal_number, data)

    return _signal_callback


def _wrap_timer_callback(f):
    @ffi.callback("int(void *data)")
    @functools.wraps(f)
    def _timer_callback(data_ptr):
        if data_ptr == ffi.NULL:
            data = None
        else:
            data = ffi.from_handle(data_ptr)

        return f(data)

    return _timer_callback


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

        self._sources = []
        weakkeydict[self] = []

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
        if data is None:
            data_ptr = ffi.NULL
        else:
            data_ptr = ffi.new_handle(data)
            weakkeydict[self].append(data_ptr)

        self._callback_store = callback_ffi = _wrap_fd_callback(callback)
        # weakkeydict[self].append(callback_ffi)

        mask = [m.value for m in mask]
        mask = functools.reduce(lambda x, y: x | y, mask)

        event_source_cdata = lib.wl_event_loop_add_fd(self._ptr, fd, mask, callback_ffi, data_ptr)
        event_source = EventSource(event_source_cdata)
        self._sources.append(event_source)

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
        if data is None:
            data_ptr = ffi.NULL
        else:
            data_ptr = ffi.new_handle(data)
            weakkeydict[self].append(data_ptr)

        callback_ffi = _wrap_signal_callback(callback)
        weakkeydict[self].append(callback_ffi)

        event_source_cdata = lib.wl_event_loop_add_signal(self._ptr, signal_number, callback_ffi, data_ptr)
        event_source = EventSource(event_source_cdata)
        self._sources.append(event_source)

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
        if data is None:
            data_ptr = ffi.NULL
        else:
            data_ptr = ffi.new_handle(data)
            weakkeydict[self].append(data_ptr)

        callback_ffi = _wrap_timer_callback(callback)
        weakkeydict[self].append(callback_ffi)

        event_source_cdata = lib.wl_event_loop_add_timer(self._ptr, callback_ffi, data_ptr)
        event_source = EventSource(event_source_cdata)
        self._sources.append(event_source)

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
