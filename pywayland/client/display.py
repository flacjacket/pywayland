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

import functools

from pywayland import ffi, lib
from pywayland.protocol.wayland import Display as _Display


def ensure_connected(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._ptr is None:
            raise ValueError("Invalid display")
        return func(self, *args, **kwargs)
    return wrapper


class Display(_Display.proxy_class):
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
    glSwapBuffers() for the Wayland platform. This function might need to block
    until a frame callback is received, but dispatching the default ueue could
    cause an event handler on the client to start drawing gain.  This problem
    is solved using another event queue, so that only the events handled by the
    EGL code are dispatched during the block.
    """
    def __init__(self):
        # Initially, we have no pointer
        super(Display, self).__init__(None)
        # we need to track event queues, ensure they are all deleted before us
        self.event_queues = []

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
            self._ptr = lib.wl_display_connect_to_fd(name_or_fd)
        else:
            if name_or_fd is None:
                name = ffi.NULL
            else:
                name = name_or_fd.encode()
            self._ptr = lib.wl_display_connect(name)

        if self._ptr == ffi.NULL:
            raise Exception

    def disconnect(self):
        """Close a connection to a Wayland display

        Close the connection to display and free all resources associated with
        it.
        """
        if self._ptr:
            # we need to be sure the event queues are destroyed before disconnecting
            for eq in self.event_queues[:]:
                eq.destroy()
            if self.event_queues:
                raise ValueError("Unable to destroy all event queues attached to this object")

            lib.wl_display_disconnect(self._ptr)
            self._ptr = None

    @ensure_connected
    def get_fd(self):
        """Get a display context's file descriptor

        Return the file descriptor associated with a display so it can be
        integrated into the client's main loop.
        """
        return lib.wl_display_get_fd(self._ptr)

    @ensure_connected
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

        .. seealso::

            :meth:`Display.dispatch_pending()`,
            :meth:`Display.dispatch_queue()`
        """
        return lib.wl_display_dispatch(self._ptr)

    @ensure_connected
    def dispatch_pending(self):
        """Dispatch default queue events without reading from the display fd

        This function dispatches events on the main event queue. It does not
        attempt to read the display fd and simply returns zero if the main
        queue is empty, i.e., it doesn't block.

        This is necessary when a client's main loop wakes up on some fd other
        than the display fd (network socket, timer fd, etc) and calls
        :meth:`Display.dispatch_queue()` from that callback. This may queue up
        events in other queues while reading all data from the display fd.
        When the main loop returns from the handler, the display fd
        no longer has data, causing a call to poll (or similar functions) to
        block indefinitely, even though there are events ready to dispatch.

        To proper integrate the wayland display fd into a main loop, the
        client should always call :meth:`Display.dispatch_pending()` and then
        :meth:`Display.flush()` prior to going back to sleep. At that point,
        the fd typically doesn't have data so attempting I/O could block, but
        events queued up on the default queue should be dispatched.

        A real-world example is a main loop that wakes up on a timerfd (or a
        sound card fd becoming writable, for example in a video player), which
        then triggers GL rendering and eventually eglSwapBuffers().
        eglSwapBuffers() may call :meth:`Display.dispatch_queue()` if it didn't
        receive the frame event for the previous frame, and as such queue
        events in the default queue.

        :returns: The number of dispatched events or -1 on failure

        .. seealso::

            :meth:`Display.dispatch()`, :meth:`Display.dispatch_queue()`,
            :meth:`Display.flush()`
        """
        return lib.wl_display_dispatch_pending(self._ptr)

    @ensure_connected
    def dispatch_queue(self, queue):
        """Dispatch events in an event queue

        Dispatch all incoming events for objects assigned to the given event
        queue. On failure -1 is returned and errno set appropriately.

        The behaviour of this function is exactly the same as the behaviour of
        :meth:`Display.dispatch()`, but it dispatches events on given queue,
        not on the default queue.

        This function blocks if there are no events to dispatch (if there are,
        it only dispatches these events and returns immediately).  When this
        function returns after blocking, it means that it read events from
        display's fd and queued them to appropriate queues.  If among the
        incoming events were some events assigned to the given queue, they are
        dispatched by this moment.

        .. note::

            Since Wayland 1.5 the display has an extra queue for its own events
            (i.e. delete_id). This queue is dispatched always, no matter what
            queue we passed as an argument to this function.  That means that
            this function can return non-0 value even when it haven't
            dispatched any event for the given queue.

        This function has the same constrains for using in multi-threaded apps
        as :meth:`Display.dispatch()`.

        :param queue: The event queue to dispatch
        :type queue: :class:`~pywayland.client.EventQueue`
        :returns: The number of dispatched events on success or -1 on failure

        .. seealso::

            :meth:`Display.dispatch()`, :meth:`Display.dispatch_pending()`
        """
        return lib.wl_display_dispatch_queue(self._ptr, queue._ptr)

    @ensure_connected
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
        return lib.wl_display_flush(self._ptr)

    @ensure_connected
    def roundtrip(self):
        """Block until all pending request are processed by the server

        This function blocks until the server has processed all currently
        issued requests by sending a request to the display server and waiting
        for a reply before returning.

        This function uses wl_display_dispatch_queue() internally. It is not
        allowed to call this function while the thread is being prepared for
        reading events, and doing so will cause a dead lock.

        .. note::

            This function may dispatch other events being received on the
            default queue.

        :returns: The number of dispatched events on success or -1 on failure
        """
        return lib.wl_display_roundtrip(self._ptr)

    @ensure_connected
    def roundtrip_queue(self, queue):
        """Block until all pending request are processed by the server

        This function blocks until the server has processed all currently
        issued requests by sending a request to the display server and waiting
        for a reply before returning.

        This function uses wl_display_dispatch_queue() internally. It is not
        allowed to call this function while the thread is being prepared for
        reading events, and doing so will cause a dead lock.

        .. note::

            This function may dispatch other events being received on the given queue.

        .. seealso::

            :meth:`Display.roundtrip()`

        :param queue: The queue on which to run the roundtrip
        :type queue: :class:`~pywayland.client.EventQueue`
        :returns: The number of dispatched events on success or -1 on failure
        """
        return lib.wl_display_roundtrip_queue(self._ptr, queue._ptr)
