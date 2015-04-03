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

from .argument import Argument


class Method(object):
    """Scanner for methods

    Corresponds to event and requests defined on an interface
    """
    def __init__(self, method, opcode):
        self._method = method
        self.name = method.attrib['name']

        self.type = method.attrib['type'] if 'type' in method.attrib else None
        self.since = method.attrib['since'] if 'since' in method.attrib else None

        self.opcode = opcode

        # 'global' is a protected name, so append '_'
        if self.name == 'global':
            self.name += '_'

    def scan(self):
        """Scan the method"""
        description = self._method.find('description')
        self.summary = description.attrib['summary']
        if description.text:
            self.description = description.text.strip()
        else:
            self.description = None

        self.args = [Argument(arg) for arg in self._method.findall('arg')]

        for arg in self.args:
            arg.scan()

    def get_imports(self, this_interface):
        """Get the imports required for each of the interfaces"""
        return [arg.get_interface() for arg in self.args
                if arg.interface and arg.interface != this_interface]

    def interface_types(self):
        """Generator of the types (for the wl_interface)"""
        for arg in self.args:
            if arg.interface:
                yield arg.get_interface()
            else:
                if arg.type == 'new_id':
                    yield 'None'
                    yield 'None'
                yield 'None'

    def output(self, printer, in_class):
        """Generate the output for the given method to the printer"""
        signature = ''.join(arg.signature for arg in self.args)
        if self.since and int(self.since) > 1:
            signature = self.since + signature
        args = ', '.join(self.method_args())
        types = ', '.join(self.interface_types())

        printer('@{}.{}("{}", [{}])'.format(
            in_class, self.method_type, signature, types)
        )
        if args:
            printer('def {}(self, {}):'.format(self.name, args))
        else:
            printer('def {}(self):'.format(self.name))
        printer.inc_level()

        # Write the documentation
        self.output_doc(printer)
        # Write out the body of the method
        self.output_body(printer)
        printer.dec_level()

    def output_doc(self, printer):
        """Output the documentation for the interface"""
        if self.description or self.args:
            printer.doc('"""{}'.format(self.summary.capitalize()))
        else:
            # This is a one-line docstring
            printer.doc('"""{}"""'.format(self.summary.capitalize()))
            return

        if self.description:
            printer()
            for line in self.description.split('\n'):
                printer.doc(line.strip())
        # Parameter and returns documentation
        if self.args:
            printer()
            self.output_doc_param(printer)
            self.output_doc_ret(printer)
        printer('"""')
