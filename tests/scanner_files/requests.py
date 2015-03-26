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

from pywayland.interface import Interface, InterfaceMeta
from .core import Core
from .events import Events

import six


@six.add_metaclass(InterfaceMeta)
class Requests(Interface):
    """request object

    The interface object with the different types of requests.
    """
    name = "wl_requests"
    version = 2


@Requests.request("niuh", [Core, None, None, None])
def make_request(self, the_int, the_uint, the_fd):
    """a request

    The request asks the server for an event.

    :param the_int:
    :type the_int: `int`
    :param the_uint: the arg summary
    :type the_uint: `uint`
    :param the_fd:
    :type the_fd: `fd`
    :returns: :class:`Core`
    """
    id = self._marshal_constructor(0, Core, the_int, the_uint, the_fd)
    return id


@Requests.request("", [])
def no_args(self):
    """request with no args

    A request method that does not have any arguments.
    """
    self._marshal(1)


@Requests.request("n", [Core])
def create_id(self):
    """create an id

    With a description

    :returns: :class:`Core`
    """
    id = self._marshal_constructor(2, Core)
    return id


@Requests.request("n", [Core])
def create_id2(self):
    """create an id without a description

    :returns: :class:`Core`
    """
    id = self._marshal_constructor(3, Core)
    return id


@Requests.request("u?s", [None, None])
def allow_null(self, serial, mime_type):
    """request that allows for null arguments

    A request where one of the arguments is allowed to be null.

    :param serial:
    :type serial: `uint`
    :param mime_type:
    :type mime_type: `string` or `None`
    """
    self._marshal(4, serial, mime_type)


@Requests.request("n?o", [Events, Core])
def make_import(self, object):
    """request that causes an import

    A request method that causes an imoprt of other interfaces, both as a
    new_id and as an object.

    :param object:
    :type object: :class:`Core` or `None`
    :returns: :class:`Events`
    """
    id = self._marshal_constructor(5, Events, object)
    return id


@Requests.request("2", [])
def versioned(self):
    """a versioned request

    A request that is versioned.
    """
    self._marshal(6)


@Requests.request("usun", [None, None, None, None])
def new_id_no_interface(self, name, interface, version):
    """create a new id, but with no interface

    A method with an argument for a new_id, but with no corresponding
    interface (c.f. wl_registry.bind).

    :param name:
    :type name: `uint`
    :param interface: Interface name
    :type interface: `string`
    :param version: Interface version
    :type version: `int`
    :returns: :class:`Proxy` of specified Interface
    """
    id = self._marshal_constructor(7, interface, name, interface.name, version)
    return id


Requests._gen_c()
