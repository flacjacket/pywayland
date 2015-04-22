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

from pywayland.interface import Interface
from .core import Core
from .requests import Requests


class Events(Interface):
    """Events object

    The interface object with the different types of events.
    """
    name = "wl_events"
    version = 2


@Events.event("niuh", [Requests, None, None, None])
def send_event(self, id, the_int, the_uint, the_fd):
    """Send the data

    Request for data from the client.  Send the data as the
    specified mime type over the passed file descriptor, then
    close it.

    :param id:
    :type id: :class:`~pywayland.protocol.requests.Requests`
    :param the_int:
    :type the_int: `int`
    :param the_uint: the arg summary
    :type the_uint: `uint`
    :param the_fd:
    :type the_fd: `fd`
    """
    self._post_event(0, id, the_int, the_uint, the_fd)


@Events.event("", [])
def no_args(self):
    """Event with no args

    An event method that does not have any arguments.
    """
    self._post_event(1)


@Events.event("n", [Core])
def create_id(self, id):
    """Create an id

    With a description

    :param id:
    :type id: :class:`~pywayland.protocol.core.Core`
    """
    self._post_event(2, id)


@Events.event("n", [Core])
def create_id2(self, id):
    """Create an id without a description

    :param id:
    :type id: :class:`~pywayland.protocol.core.Core`
    """
    self._post_event(3, id)


@Events.event("?s", [None])
def allow_null_event(self, null_string):
    """A event with an allowed null argument

    An event where one of the arguments is allowed to be null.

    :param null_string:
    :type null_string: `string` or `None`
    """
    self._post_event(4, null_string)


@Events.event("n?o", [Requests, Core])
def make_import(self, id, object):
    """Event that causes an import

    An event method that causes an imoprt of other interfaces

    :param id:
    :type id: :class:`~pywayland.protocol.requests.Requests`
    :param object:
    :type object: :class:`~pywayland.protocol.core.Core` or `None`
    """
    self._post_event(5, id, object)


@Events.event("2", [])
def versioned(self):
    """A versioned event

    An event that is versioned.
    """
    self._post_event(6)


Events._gen_c()
