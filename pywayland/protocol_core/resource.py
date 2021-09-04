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

from typing import Optional, Type, TYPE_CHECKING

from pywayland import ffi, lib
from pywayland.dispatcher import Dispatcher
from pywayland.utils import ensure_valid
from pywayland.server.client import Client

if TYPE_CHECKING:
    from .interface import Interface  # noqa: F401


class Resource:
    """A server-side Interface object for the client

    Not created directly, created from the
    :class:`~pywayland.interface.Interface` object.

    :param client: The client that the Resource is for
    :type client: :class:`~pywayland.server.Client` or cdata for ``wl_client *``
    :param version: The version to use for the
                    :class:`~pywayland.interface.Interface`, uses current
                    version if not specified
    :type version: `int`
    :param id: The id for the item
    :type id: `int`
    """

    interface: Type["Interface"]

    def __init__(self, client, version=None, id=0) -> None:
        if version is None:
            version = self.interface.version

        self.version = version
        self.dispatcher = Dispatcher(self.interface.requests, destructor=True)

        if isinstance(client, Client):
            client_ptr = client._ptr
        else:
            client_ptr = client
        assert client_ptr is not None

        self._ptr: Optional["ffi.ResourceCData"] = lib.wl_resource_create(
            client_ptr, self.interface._ptr, version, id
        )
        self.id = lib.wl_resource_get_id(self._ptr)

        if self.dispatcher is not None:
            self._handle = ffi.new_handle(self)
            lib.wl_resource_set_dispatcher(
                self._ptr,
                lib.dispatcher_func,
                ffi.NULL,
                self._handle,
                lib.resource_destroy_func,
            )

    def destroy(self) -> None:
        """Destroy the Resource"""
        if self._ptr:
            lib.wl_resource_destroy(self._ptr)
            self._ptr = None

    @ensure_valid
    def add_destroy_listener(self, listener) -> None:
        """Add a listener for the destroy signal

        :param listener: The listener object
        :type listener: :class:`~pywayland.server.Listener`
        """
        assert self._ptr is not None
        lib.wl_resource_add_destroy_listener(self._ptr, listener._ptr)

    @ensure_valid
    def _post_event(self, opcode, *args) -> None:
        # Create wl_argument array
        args_ptr = self.interface.events[opcode].arguments_to_c(*args)
        # Make the cast to a wl_resource
        assert self._ptr is not None
        resource: ffi.ResourceCData = ffi.cast("struct wl_resource *", self._ptr)  # type: ignore[assignment]

        lib.wl_resource_post_event_array(resource, opcode, args_ptr)

    @ensure_valid
    def _post_error(self, code, msg="") -> None:
        assert self._ptr is not None
        lib.wl_resource_post_error(self._ptr, code, msg.encode())
