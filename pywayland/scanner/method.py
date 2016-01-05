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

# For 'new_id' types with no 'interface'
NO_IFACE = 'interface'
NO_IFACE_VERSION = 'version'


class Method(object):
    """Scanner for methods

    Corresponds to event and requests defined on an interface
    """

    def __init__(self, method, iface_name, opcode):
        super(Method, self).__init__(method)

        self.opcode = opcode
        self.interface = iface_name

        # 'global' is a protected name, so append '_'
        if self.name == 'global':
            self.name += '_'

    @property
    def imports(self):
        """Get the imports required for each of the interfaces"""
        imports = []
        for arg in self.arg:
            if arg.interface and arg.interface != self.interface:
                # External protocols can import from main Wayland protocols
                if arg.interface.split('_')[0] != self.interface.split('_')[0]:
                    assert arg.interface.split('_')[0] == 'wl', "Don't know how to import interface"
                    prefix = arg.interface.split('_')[0]
                    import_path = '..wayland.{}'.format(arg.interface_class.lower())
                    import_class = '{0} as {1}_{0}'.format(arg.interface_class, prefix)
                else:
                    import_path = '.{}'.format(arg.interface_class.lower())
                    import_class = arg.interface_class
                imports.append((import_path, import_class))

        return imports

    def output(self, printer, in_class):
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
        self.output_doc(printer)
        # Write out the body of the method
        self.output_body(printer)
        printer.dec_level()

    def output_doc(self, printer):
        """Output the documentation for the interface"""
        if self.description:
            self.description.output(printer)
        else:
            printer('"""' + self.name)
        # Parameter and returns documentation
        if self.arg:
            printer()
            self.output_doc_params(printer)
        printer('"""')

    def output_doc_param(self, printer):
        # Subclasses must define this to output the parameters
        raise NotImplementedError()
