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

import six


@six.add_metaclass(InterfaceMeta)
class Destructor(Interface):
    """destructor object

    An interface object with a destructor request.

    And a multiline description.
    """
    name = "wl_destructor"
    version = 1


@Destructor.request("niiiiu", [Destructor, None, None, None, None, None])
def create_interface(self, x, y, width, height, format):
    """create another interface

    Create a wl_destructor_interface object

    :param x:
    :type x: `int`
    :param y:
    :type y: `int`
    :param width:
    :type width: `int`
    :param height:
    :type height: `int`
    :param format:
    :type format: `uint`
    :returns: :class:`Destructor`
    """
    id = self._marshal_constructor(0, Destructor, x, y, width, height, format)
    return id


@Destructor.request("", [])
def destroy(self):
    """destroy the interface

    Destroy the created interface.
    """
    self._marshal(1)
    self._destroy()


Destructor._gen_c()
