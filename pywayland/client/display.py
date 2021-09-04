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

from typing import Optional, Union, TYPE_CHECKING
from weakref import WeakSet

from pywayland import ffi, lib
from pywayland.client.eventqueue import EventQueue
from pywayland.utils import ensure_valid
from pywayland.protocol.wayland import WlDisplay

if TYPE_CHECKING:
    # introduced in standard library in Python 3.8
    from typing_extensions import Literal  # noqa: F401


class Display(WlDisplay.proxy_class):  # type: ignore
    """Represents a connection to the compositor

    A :class:`Display` object represents a client connection to a Wayland
    compositor.  The connection and the corresponding Wayland object are
    created with :func:`Display.connect`.  The display must be connected before
    it can be used.  A connection is terminated using
    :func:`Display.disconnect`.

    A :class:`Display` is also used as the
    :class:`~pywayland.client.proxy.Proxy` for the
    :class:`pywayland.protocol.wayland.WlDisplay` protocol object on the
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

    :param name_or_fd:
        Either the name of the display to create or the file descriptor to
        connect the display to.  If not specified, then use the default name,
        generally ``wayland-0``
    :type name_or_fd:
        ``int`` or ``str``
    """

    def __init__(self, name_or_fd: Optional[Union[int, str]] = None) -> None:
        """Constructor for the Display object"""
        super().__init__(None)

        self._children: WeakSet = WeakSet()
        self._name_or_fd = name_or_fd
        self._ptr: Optional["ffi.DisplayCData"] = None

    def __enter__(self) -> "Display":
        """Connect to the display in a context manager"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> "Literal[False]":
        """Disconnect from the display"""
        self.disconnect()
        return False

    def connect(self) -> None:
        """Connect to a Wayland display

        Connect to the Wayland display by name of fd.  An `int` parameter opens
        the connection using the file descriptor.  The :class:`Display` takes
        ownership of the fd and will close it when the display is destroyed.
        The fd will also be closed in case of failure.  A string will open the
        display of the given name.  If name is ``None``, its value will be
        replaced with the ``WAYLAND_DISPLAY`` environment variable if it is
        set, otherwise display ``"wayland-0"`` will be used.
        """
        if isinstance(self._name_or_fd, int):
            # argument passed is a file descriptor
            self._ptr = lib.wl_display_connect_to_fd(self._name_or_fd)
        else:
            # connect using string by name, or use default
            if self._name_or_fd is None:
                name: Union["ffi.CData", bytes] = ffi.NULL
            else:
                name = self._name_or_fd.encode()
            self._ptr = lib.wl_display_connect(name)

        if self._ptr == ffi.NULL:
            raise ValueError("Unable to connect to display")

        self._ptr = ffi.gc(self._ptr, lib.wl_display_disconnect)

    def disconnect(self) -> None:
        """Close a connection to a Wayland display

        Close the connection to display and free all resources associated with
        it.
        """
        if self._ptr:
            # we need to be sure the event queues and proxies are destroyed
            # before we disconnect the client
            for obj in self._children:
                if not obj.destroyed:
                    obj.destroy()

            # run destructor and remove it
            ffi.release(self._ptr)
            self._ptr = None

    _destroy = disconnect

    @ensure_valid
    def get_fd(self) -> int:
        """Get a display context's file descriptor

        Return the file descriptor associated with a display so it can be
        integrated into the client's main loop.
        """
        assert self._ptr is not None
        return lib.wl_display_get_fd(self._ptr)

    @ensure_valid
    def dispatch(
        self, *, block: bool = False, queue: Optional[EventQueue] = None
    ) -> int:
        """Process incoming events

        If block is `False`, it does not attempt to read the display fd or
        event queue and simply returns zero if the queue is empty.

        If the given queue is empty and `block` is `True`, this function blocks
        until there are events to be read from the display fd. Events are read
        and queued on the appropriate event queues. Finally, events on the
        default event queue are dispatched.

        .. note::

            It is not possible to check if there are events on the queue or
            not.
        """
        assert self._ptr is not None
        if block:
            if queue is None:
                ret = lib.wl_display_dispatch(self._ptr)
            else:
                assert queue._ptr is not None
                ret = lib.wl_display_dispatch_queue(self._ptr, queue._ptr)
        else:
            if queue is None:
                ret = lib.wl_display_dispatch_pending(self._ptr)
            else:
                assert queue._ptr is not None
                ret = lib.wl_display_dispatch_queue_pending(self._ptr, queue._ptr)

        if ret == -1:
            err = lib.wl_display_get_error(self._ptr)
            raise RuntimeError("Failed with error: {}".format(err))

        return ret

    @ensure_valid
    def roundtrip(self, *, queue: Optional[EventQueue] = None) -> int:
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

        :param queue: The queue on which to run the roundtrip, if not given,
                      uses the default queue.
        :type queue: :class:`~pywayland.client.EventQueue`
        :returns: The number of dispatched events on success or -1 on failure
        """
        assert self._ptr is not None
        if queue is None:
            return lib.wl_display_roundtrip(self._ptr)
        else:
            assert queue._ptr is not None
            return lib.wl_display_roundtrip_queue(self._ptr, queue._ptr)

    @ensure_valid
    def read(self, *, queue: Optional[EventQueue] = None) -> None:
        """Read events from display file descriptor

        Calling this function will result in data available on the display file
        descriptor being read and read events will be queued on their
        corresponding event queues.

        :param queue: If specified, queue the events onto the given event
                      queue, otherwise the default display queue will be used.
        """
        assert self._ptr is not None
        while True:
            if queue is None:
                prepared = lib.wl_display_prepare_read(self._ptr)
            else:
                assert queue._ptr is not None
                prepared = lib.wl_display_prepare_read_queue(self._ptr, queue._ptr)

            if prepared == 0:
                break

            # TODO: add a blocking/non-blocking condition here

            self.dispatch(block=False, queue=queue)

        status = lib.wl_display_read_events(self._ptr)
        if status != 0:
            raise RuntimeError("Failed to read events")

    @ensure_valid
    def flush(self) -> int:
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
        assert self._ptr is not None
        return lib.wl_display_flush(self._ptr)
