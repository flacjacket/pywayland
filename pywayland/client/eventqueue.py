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

import functools
from weakref import WeakKeyDictionary

weakkeydict = WeakKeyDictionary()  # type: WeakKeyDictionary


def _event_queue_destroy(display, cdata):
    # we should be careful that the display is still around
    if display._ptr is None:
        return
    lib.wl_event_queue_destroy(cdata)


class EventQueue:
    """A queue for wl_proxy object events.

    Event queues allows the events on a display to be handled in a thread-safe
    manner. See :class:`~pywayland.client.Display` for details.
    """
    def __init__(self, display):
        # lets check that we attach to an ok display
        if display._ptr is None or display._ptr == ffi.NULL:
            raise ValueError("Display object not connected")

        ptr = lib.wl_display_create_queue(display._ptr)

        # create a destructor, save data and display
        destructor = functools.partial(_event_queue_destroy, display)
        self._ptr = ffi.gc(ptr, destructor)
        self._display = display

        display._children.add(self)

        weakkeydict[self._ptr] = display

    def destroy(self):
        """Destroy an event queue

        Destroy the given event queue. Any pending event on that queue is
        discarded.

        The wl_display object used to create the queue should not be destroyed
        until all event queues created with it are destroyed with this
        function.
        """
        if self._ptr is not None and self._display is not None:
            # run destroyer and remove it from the _ffi object
            _event_queue_destroy(self._display, self._ptr)
            ffi.gc(self._ptr, None)

            # delete the pointer and the reference to the display
            self._ptr = None
            self._display = None
