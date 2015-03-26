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
from pywayland.protocol.display import Display as _Display

from .proxy import Proxy, _dispatcher


class Display(Proxy):
    _interface = _Display
    _ptr = None

    def __init__(self):
        """Represents a connection to the compositor

        A wl_display object represents a client connection to a Wayland
        compositor. It is created with either wl_display_connect() or
        wl_display_connect_to_fd(). A connection is terminated using
        wl_display_disconnect().

        A wl_display is also used as the wl_proxy for the wl_display singleton
        object on the compositor side.

        A wl_display object handles all the data sent from and to the
        compositor. When a wl_proxy marshals a request, it will write its wire
        representation to the display's write buffer. The data is sent to the
        compositor when the client calls wl_display_flush().

        Incoming data is handled in two steps: queueing and dispatching. In the
        queue step, the data coming from the display fd is interpreted and
        added to a queue. On the dispatch step, the handler for the incoming
        event set by the client on the corresponding wl_proxy is called.

        A wl_display has at least one event queue, called the _default queue_.
        Clients can create additional event queues with
        wl_display_create_queue() and assign wl_proxy's to it. Events occurring
        in a particular proxy are always queued in its assigned queue.  A
        client can ensure that a certain assumption, such as holding a lock or
        running from a given thread, is true when a proxy event handler is
        called by assigning that proxy to an event queue and making sure that
        this queue is only dispatched when the assumption holds.

        The default queue is dispatched by calling wl_display_dispatch().  This
        will dispatch any events queued on the default queue and attempt to
        read from the display fd if it's empty. Events read are then queued on
        the appropriate queues according to the proxy assignment.

        A user created queue is dispatched with wl_display_dispatch_queue().
        This function behaves exactly the same as wl_display_dispatch() but it
        dispatches given queue instead of the default queue.

        A real world example of event queue usage is Mesa's implementation of
        glSwapBuffers() for the Wayland platform. This function might need o
        block until a frame callback is received, but dispatching the default
        ueue could cause an event handler on the client to start drawing gain.
        This problem is solved using another event queue, so that only he
        events handled by the EGL code are dispatched during the block.

        This creates a problem where a thread dispatches a non-default queue,
        reading all the data from the display fd. If the application would call
        _poll(2)_ after that it would block, even though there might be events
        queued on the default queue. Those events should be dispatched with
        wl_display_dispatch_(queue_)pending() before flushing and blocking.
        """
        super().__init__()

    def __del__(self):
        self.disconnect()

    def connect(self, name_or_fd=None):
        """Connect to a Wayland display

        Connect to the Wayland display by name of fd.  An `int` parameter opens
        the connection using the file descriptor.  The wl_display takes
        ownership of the fd and will close it when the display is destroyed.
        The fd will also be closed in case of failure.  A string will open the
        display of the given name.  If name is None, its value will be replaced
        with the WAYLAND_DISPLAY environment variable if it is set, otherwise
        display "wayland-0" will be used.
        """
        if isinstance(name_or_fd, int):
            self._ptr = C.wl_display_connect_to_fd(name_or_fd)
        else:
            if name_or_fd is None:
                name = ffi.NULL
            else:
                name = name_or_fd.encode()
            self._ptr = C.wl_display_connect(name)

        if self._ptr == ffi.NULL:
            raise Exception

        _ptr = ffi.cast('struct wl_proxy *', self._ptr)
        C.wl_proxy_add_dispatcher(_ptr, _dispatcher, self._handle, ffi.NULL)

    def disconnect(self):
        """Close a connection to a Wayland display

        Close the connection to display and free all resources associated with
        it.
        """
        if self._ptr:
            C.wl_display_disconnect(self._ptr)
            self._ptr = None

    def get_fd(self):
        """Get a display context's file descriptor

        Return the file descriptor associated with a display so it can be
        integrated into the client's main loop.
        """
        return C.wl_display_get_fd(self._ptr)

    def dispatch(self):
        """Process incoming events

        Dispatch the display's default event queue.

        If the default event queue is empty, this function blocks until there
        are events to be read from the display fd. Events are read and queued
        on the appropriate event queues. Finally, events on the default event
        queue are dispatched.

        In multi-threaded environment, programmer may want to use
        wl_display_read_events(). However, use of wl_display_read_events() must
        not be mixed with wl_display_dispatch(). See wl_display_read_events()
        and wl_display_prepare_read() for more details.

        Note: It is not possible to check if there are events on the queue or
        not. For dispatching default queue events without blocking, see
        wl_display_dispatch_pending().
        """
        return C.wl_display_dispatch(self._ptr)

    def flush(self):
        """Send all buffered requests on the display to the server

        Send all buffered data on the client side to the server. Clients
        should call this function before blocking. On success, the number
        of bytes sent to the server is returned. On failure, this
        function returns -1 and errno is set appropriately.

        wl_display_flush() never blocks.  It will write as much data as
        possible, but if all data could not be written, errno will be set
        to EAGAIN and -1 returned.  In that case, use poll on the display
        file descriptor to wait for it to become writable again.
        """
        return C.wl_display_flush(self._ptr)

    def roundtrip(self):
        """Block until all pending request are processed by the server

        Blocks until the server process all currently issued requests and
        sends out pending events on the default event queue.
        """
        return C.wl_display_roundtrip(self._ptr)

for msg in _Display.requests:
    setattr(Display, msg.name, msg._func)
