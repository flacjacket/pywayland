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

from .element import Element, Attribute, Child

from .description import Description
from .enum import Enum
from .event import Event
from .request import Request

import itertools


class Interface(Element):
    attributes = [Attribute('name', True), Attribute('version', True)]
    children = [
        Child('description', Description, False, False),
        Child('enum', Enum, False, True),
        # Child('request', Request, False, True),
        # Child('event', Event, False, True)
    ]

    def __init__(self, iface):
        """Scanner for interface objects

        Required attributes: `name` and `version`

        Child elements: `description`, `request`, `event`, `enum`
        """
        super(Interface, self).__init__(iface)

        # Requests and events need special handling to get the opcode and
        # interface name
        self.event = [
            Event(event, self.name, i)
            for i, event in enumerate(iface.findall('event'))
        ]
        self.request = [
            Request(request, self.name, i)
            for i, request in enumerate(iface.findall('request'))
        ]

    @property
    def class_name(self):
        """Returns the name of the class of the interface

        Camel cases the name of the interface, to be used as the class name.
        """
        return ''.join(x.capitalize() for x in self.name.split('_'))

    def output(self, printer, module_imports):
        """Generate the output for the interface to the printer"""
        # Imports
        imports = set(
            _import
            for method in itertools.chain(self.request, self.event)
            for _import in method.imports(module_imports)
        )
        printer('from pywayland.interface import Interface')
        for module, import_ in sorted(imports):
            printer('from {} import {}'.format(module, import_))
        if self.enum:
            printer()
            printer('import enum')
        printer()
        printer()

        # Class definition
        printer('class {}(Interface):'.format(self.class_name))
        with printer.indented():
            # Docstring
            if self.description:
                self.description.output(printer)
                printer('"""')

            # Class attributes
            printer('name = "{}"'.format(self.name))
            printer('version = {}'.format(self.version))

            # Enums
            for enum in self.enum:
                printer()
                enum.output(printer)

        # Events and requests
        for method in itertools.chain(self.request, self.event):
            printer()
            printer()
            method.output(printer, self.class_name, module_imports)

        printer()
        printer()
        printer('{}._gen_c()'.format(self.class_name))
