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

NO_IFACE_NAME = 'interface'


class Argument(object):
    def __init__(self, arg):
        """Argument to a request or event method

        Required attributes: `name` and `type`

        Optional attributes: `summary`, `interface`, and `allow-null`

        Child elements: `description`
        """
        self._arg = arg
        self.name = arg.attrib['name']
        self.type = arg.attrib['type']
        self.summary = arg.attrib['summary'] if 'summary' in arg.attrib else None
        self.interface = arg.attrib['interface'] if 'interface' in arg.attrib else None
        self.allow_null = arg.attrib['allow-null'] == 'true' if 'allow-null' in arg.attrib else False

    def scan(self):
        """Scan the argument"""
        # Currently, no arguments have description elements, but the dtd says
        # they may, they should be parsed here
        pass

    def get_interface(self):
        """Returns the Interface class name

        Gives the class name for the Interface coresponding to the type of the
        argument.
        """
        return ''.join(x.capitalize() for x in self.interface.split('_')[1:])

    @property
    def signature(self):
        """Return the signature of the argument

        Return the string corresponding to the signature of the argument as it
        appears in the signature of the wl_message struct.
        """
        null_string = '?' if self.allow_null else ''
        return null_string + self.type_to_string()

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

    def output_doc_param(self, printer):
        """Document the argument as a parameter"""
        # Output the parameter and summary
        if self.summary:
            printer(':param {}: {}'.format(self.name, self.summary))
        else:
            printer(':param {}:'.format(self.name))

        # Determine the type to be output
        if self.interface:
            arg_type = ':class:`{}`'.format(self.get_interface())
        else:
            arg_type = '`{}`'.format(self.type)

        # Output the parameter type
        if self.allow_null:
            printer(':type {}: {} or `None`'.format(self.name, arg_type))
        else:
            printer(':type {}: {}'.format(self.name, arg_type))

    def output_doc_ret(self, printer):
        """Document the argument as a return"""
        # Determine the type to be output
        if self.interface:
            arg_type = ':class:`{}`'.format(self.get_interface())
        else:
            # Only new_id's are returned, the only corner case here is for
            # wl_registry.bind, so no interface => Proxy
            arg_type = ':class:`Proxy` of specified Interface'

        # Output the type and summary
        if self.summary:
            printer(':returns: {} -- {}'.format(arg_type, self.summary))
        else:
            printer(':returns: {}'.format(arg_type))
