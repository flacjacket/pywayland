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
from .description import Description
from .element import Child, Element

# For 'new_id' types with no 'interface'
NO_IFACE = 'interface'
NO_IFACE_VERSION = 'version'


class Method(Element):
    """Scanner for methods

    Corresponds to event and requests defined on an interface
    """

    children = [
        Child('description', Description, False, False),
        Child('arg', Argument, False, True),
    ]

    def __init__(self, method, iface_name, opcode):
        super(Method, self).__init__(method)

        self.opcode = opcode
        self.interface = iface_name

        # some methods are protected names, so append '_'
        if self.name in ('global', 'import'):
            self.name += '_'

    def imports(self, module_imports):
        """Get the imports required for each of the interfaces"""
        interface_class = ''.join(x.capitalize() for x in self.interface.split('_'))
        current_protocol = module_imports[interface_class]

        imports = []
        for arg in self.arg:
            if arg.interface is None:
                continue

            if arg.interface == self.interface:
                continue

            import_class = arg.interface_class
            import_protocol = module_imports[import_class]

            if current_protocol == import_protocol:
                import_path = ".{}".format(arg.interface)
            else:
                import_path = "..{}".format(import_protocol)

            imports.append((import_path, import_class))

        return imports

    def output(self, printer, in_class, module_imports):
        """Generate the output for the given method to the printer"""
        # Generate the decorator for the method
        signature = ''.join(arg.signature for arg in self.arg)
        if self.since and int(self.since) > 1:
            signature = self.since + signature
        types = ', '.join(self.interface_types)

        printer('@{}.{}("{}", [{}])'.format(
            in_class, self.method_type, signature, types)
        )

        # Generate the definition of the method and args
        args = ', '.join(['self'] + list(self.method_args))
        printer('def {}({}):'.format(self.name, args))
        printer.inc_level()

        # Write the documentation
        self.output_doc(printer, module_imports)
        # Write out the body of the method
        self.output_body(printer)
        printer.dec_level()

    def output_doc(self, printer, module_imports):
        """Output the documentation for the interface"""
        if self.description:
            self.description.output(printer, module_imports)
        else:
            printer('"""' + self.name)
        # Parameter and returns documentation
        if self.arg:
            printer()
            self.output_doc_params(printer, module_imports)
        printer('"""')

    def output_doc_param(self, printer, module_imports):
        # Subclasses must define this to output the parameters
        raise NotImplementedError()
