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
    """Represents a connection to the compositor

    A :class:`Display` object represents a client connection to a Wayland
    compositor.  The connection and the corresponding Wayland object are
    created with :func:`Display.connect`.  The display must be connected before
    it can be used.  A connection is terminated using
    :func:`Display.disconnect`.

    A :class:`Display` is also used as the
    :class:`~pywayland.client.proxy.Proxy` for the (similarly named)
    :class:`pywayland.protocol.display.Display` protocol object on the
    compositor side.

    A :class:`Display` object handles all the data sent from and to the
    compositor.  When a :class:`~pywayland.client.proxy.Proxy` marshals a
    request, it will write its wire representation to the display's write
    buffer. The data is sent to the compositor when the client calls
    :func:`flush`.

    Incoming data is handled in two steps: queueing and dispatching. In the
    queue step, the data coming from the display fd is interpreted and added to
    a queue. On the dispatch step, the handler for the incoming event set by
    the client on the corresponding :class:`~pywayland.client.proxy.Proxy` is
    called.

    A :class:`Display` has at least one event queue, called the `default
    queue`.  Clients can create additional event queues with
    :func:`Display.create_queue` and assign
    :class:`~pywayland.client.proxy.Proxy`'s to it. Events occurring in a
    particular proxy are always queued in its assigned queue.  A client can
    ensure that a certain assumption, such as holding a lock or running from a
    given thread, is true when a proxy event handler is called by assigning
    that proxy to an event queue and making sure that this queue is only
    dispatched when the assumption holds.

    The default queue is dispatched by calling :func:`Display.dispatch`.  This
    will dispatch any events queued on the default queue and attempt to read
    from the display fd if it's empty. Events read are then queued on the
    appropriate queues according to the proxy assignment.

    A user created queue is dispatched with :func:`Display.dispatch_queue`.
    This function behaves exactly the same as :func:`Display.dispatch` but it
    dispatches given queue instead of the default queue.

    A real world example of event queue usage is Mesa's implementation of
    glSwapBuffers() for the Wayland platform. This function might need o block
    until a frame callback is received, but dispatching the default ueue could
    cause an event handler on the client to start drawing gain.  This problem
    is solved using another event queue, so that only he events handled by the
    EGL code are dispatched during the block.
    """
    _interface = _Display
    _ptr = None

    def __init__(self):
        super(Display, self).__init__()

    def __del__(self):
        self.disconnect()

    def connect(self, name_or_fd=None):
        """Connect to a Wayland display

        Connect to the Wayland display by name of fd.  An `int` parameter opens
        the connection using the file descriptor.  The :class:`Display` takes
        ownership of the fd and will close it when the display is destroyed.
        The fd will also be closed in case of failure.  A string will open the
        display of the given name.  If name is ``None``, its value will be
        replaced with the ``WAYLAND_DISPLAY`` environment variable if it is
        set, otherwise display ``"wayland-0"`` will be used.
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

        .. note::

            It is not possible to check if there are events on the queue or
            not. For dispatching default queue events without blocking, see
            :func:`Display.dispatch_pending`.
        """
        return C.wl_display_dispatch(self._ptr)

    def flush(self):
        """Send all buffered requests on the display to the server

        Send all buffered data on the client side to the server. Clients
        should call this function before blocking. On success, the number
        of bytes sent to the server is returned. On failure, this
        function returns -1 and errno is set appropriately.

        :func:`Display.flush` never blocks.  It will write as much data as
        possible, but if all data could not be written, errno will be set to
        EAGAIN and -1 returned.  In that case, use poll on the display file
        descriptor to wait for it to become writable again.
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
