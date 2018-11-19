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

from .element import Element, Attribute

NO_IFACE_NAME = 'interface'


class Argument(Element):
    """Argument to a request or event method

    Required attributes: `name` and `type`

    Optional attributes: `summary`, `interface`, and `allow-null`

    Child elements: `description`
    """
    attributes = [
        Attribute('name', True),
        Attribute('type', True),
        Attribute('summary', False),
        Attribute('interface', False),
        Attribute('allow-null', False),
        Attribute('enum', False)
    ]

    @property
    def interface_class(self):
        """Returns the Interface class name

        Gives the class name for the Interface coresponding to the type of the
        argument.
        """
        return ''.join(x.capitalize() for x in self.interface.split('_'))

    @property
    def signature(self):
        """Return the signature of the argument

        Return the string corresponding to the signature of the argument as it
        appears in the signature of the wl_message struct.
        """
        if self.allow_null:
            return '?' + self.type_to_string()
        else:
            return self.type_to_string()

    def type_to_string(self):
        """Translate type to signature string"""
        if self.type == 'int':
            return 'i'
        elif self.type == 'uint':
            return 'u'
        elif self.type == 'fixed':
            return 'f'
        elif self.type == 'string':
            return 's'
        elif self.type == 'object':
            return 'o'
        elif self.type == 'new_id':
            if self.interface:
                return 'n'
            else:
                return 'sun'
        elif self.type == 'array':
            return 'a'
        elif self.type == 'fd':
            return 'h'

    def output_doc_param(self, printer, module_imports):
        """Document the argument as a parameter"""
        # Output the parameter and summary
        if self.summary:
            printer.doc(':param {}: {}'.format(self.name, self.summary), module_imports)
        else:
            printer.doc(':param {}:'.format(self.name), module_imports)

        # Determine the type to be output
        if self.interface:
            arg_type = self._doc_interface(printer, module_imports)
        else:
            arg_type = '`{}`'.format(self.type)

        # Output the parameter type
        if self.allow_null:
            printer.doc(':type {}: {} or `None`'.format(self.name, arg_type), module_imports)
        else:
            printer.doc(':type {}: {}'.format(self.name, arg_type), module_imports)

    def output_doc_ret(self, printer, module_imports):
        """Document the argument as a return"""
        # Determine the type to be output
        if self.interface:
            arg_type = self._doc_interface(printer, module_imports)
        else:
            # Only new_id's are returned, the only corner case here is for
            # wl_registry.bind, so no interface => Proxy
            arg_type = ':class:`pywayland.client.proxy.Proxy` of specified Interface'

        # Output the type and summary
        if self.summary:
            printer.doc(':returns: {} -- {}'.format(arg_type, self.summary), module_imports)
        else:
            printer.doc(':returns: {}'.format(arg_type), module_imports)

    def _doc_interface(self, printer, module_imports):
        interface_class = ''.join(x.capitalize() for x in self.interface.split('_'))
        if self.interface != printer.iface_name and interface_class in module_imports:
            interface_module = module_imports[interface_class]
            return ':class:`~pywayland.protocol.{}.{}`'.format(interface_module, interface_class)
        else:
            print(interface_class)
            return ':class:`{}`'.format(interface_class)
