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

from .element import Attribute
from .method import Method

# For 'new_id' types with no 'interface'
NO_IFACE = 'interface'
NO_IFACE_VERSION = 'version'


class Request(Method):
    """Scanner for request objects (client-side method)

    Required attributes: `name`

    Optional attributes: `type` and `since`

    Child elements: `description` and `arg`
    """
    method_type = 'request'

    attributes = [
        Attribute('name', True),
        Attribute('type', False),
        Attribute('since', False)
    ]

    @property
    def new_id(self):
        for arg in self.arg:
            if arg.type == 'new_id':
                return arg

    @property
    def method_args(self):
        """Generator of the arguments to the method

        The `new_id` args are generated in marshaling the args, they do not
        appear in the args of the method.
        """
        for arg in self.arg:
            if arg.type == 'new_id':
                # An interface of known type is created for us
                if arg.interface:
                    continue
                # A `new_id` with no interface, c.f. wl_registry_bind
                # Need a string (interface name) and int (interface version)
                yield NO_IFACE
                yield NO_IFACE_VERSION
            else:
                yield arg.name

    @property
    def interface_types(self):
        """Generator of the types (for the wl_interface)"""
        for arg in self.arg:
            if arg.interface:
                yield arg.interface_class
            else:
                if arg.type == 'new_id':
                    yield 'None'
                    yield 'None'
                yield 'None'

    @property
    def marshal_args(self):
        """Arguments sent to `._marshal`"""
        for arg in self.arg:
            if arg.type == 'new_id':
                if not arg.interface:
                    yield '{}.name'.format(NO_IFACE)
                    yield NO_IFACE_VERSION
            else:
                yield arg.name

    def output_doc_params(self, printer):
        """Aguments documented as parameters

        Anything that is not a `new_id` is
        """
        ret = None
        for arg in self.arg:
            if arg.type == 'new_id':
                ret = arg
                if arg.interface:
                    continue
                printer(':param {}: Interface name'.format(NO_IFACE))
                printer(':type {}: `string`'.format(NO_IFACE))
                printer(':param {}: Interface version'.format(NO_IFACE_VERSION))
                printer(':type {}: `int`'.format(NO_IFACE_VERSION))
            else:
                arg.output_doc_param(printer)
        if ret is not None:
            ret.output_doc_ret(printer)

    def output_doc_ret(self, printer):
        """Aguments documented as return values

        Arguments of type `new_id` are returned from requests.
        """
        for arg in self.arg:
            if arg.type == 'new_id':
                arg.output_doc_ret(printer)

    def output_body(self, printer):
        """Output the body of the request to the printer"""
        if self.new_id:
            if self.new_id.interface:
                id_class = self.new_id.interface_class
            else:
                id_class = NO_IFACE
            args = ', '.join([str(self.opcode), id_class] + list(self.marshal_args))
            printer('{} = self._marshal_constructor({})'.format(
                self.new_id.name, args)
            )
            printer('return {}'.format(self.new_id.name))
        else:
            args = ', '.join([str(self.opcode)] + list(self.marshal_args))
            printer('self._marshal({})'.format(args))
            if self.type == 'destructor':
                printer('self._destroy()')
