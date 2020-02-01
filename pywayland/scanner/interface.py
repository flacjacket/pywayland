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

import itertools
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Dict, List, Optional

from .description import Description
from .element import Element
from .enum import Enum
from .event import Event
from .printer import Printer
from .request import Request


@dataclass(frozen=True)
class Interface(Element):
    name: str
    version: str
    description: Optional[Description]
    enum: List[Enum]
    event: List[Event]
    request: List[Request]

    @classmethod
    def parse(cls, element: ET.Element) -> "Interface":
        """Scanner for interface objects

        Required attributes: `name` and `version`

        Child elements: `description`, `request`, `event`, `enum`
        """
        name = cls.parse_attribute(element, "name")
        return cls(
            name=name,
            version=cls.parse_attribute(element, "version"),
            description=cls.parse_optional_child(element, Description, "description"),
            enum=cls.parse_repeated_child(element, Enum, "enum"),
            event=cls.parse_repeated_child(element, Event, "event"),
            request=cls.parse_repeated_child(element, Request, "request"),
        )

    @property
    def class_name(self) -> str:
        """Returns the name of the class of the interface

        Camel cases the name of the interface, to be used as the class name.
        """
        return "".join(x.capitalize() for x in self.name.split("_"))

    def output(self, printer: Printer, module_imports: Dict[str, str]) -> None:
        """Generate the output for the interface to the printer"""
        # Imports
        imports = set(
            _import
            for method in itertools.chain(self.request, self.event)
            for _import in method.imports(self.name, module_imports)
        )

        needs_argument_type = any(
            len(method.arg) > 0 for method in self.request
        ) or any(len(method.arg) > 0 for method in self.event)

        if self.enum:
            printer("import enum")
            printer()
        if needs_argument_type:
            printer(
                "from pywayland.protocol_core import Argument, ArgumentType, Global, Interface, Proxy, Resource"
            )
        else:
            printer(
                "from pywayland.protocol_core import Global, Interface, Proxy, Resource"
            )

        for module, import_ in sorted(imports):
            printer("from {} import {}".format(module, import_))
        printer()
        printer()

        # Class definition
        printer("class {}(Interface):".format(self.class_name))
        with printer.indented():
            # Docstring
            if self.description:
                self.description.output(printer)
                printer('"""')
                printer()

            # Class attributes
            printer('name = "{}"'.format(self.name))
            printer("version = {}".format(self.version))

            # Enums
            for enum in self.enum:
                printer()
                enum.output(printer)

        proxy_class_name = f"{self.class_name}Proxy"
        resource_class_name = f"{self.class_name}Resource"
        global_class_name = f"{self.class_name}Global"

        printer()
        printer()
        printer(f"class {proxy_class_name}(Proxy):")
        with printer.indented():
            printer(f"interface = {self.class_name}")
            for opcode, request in enumerate(self.request):
                printer()
                request.output(printer, opcode, self.class_name, module_imports)

        printer()
        printer()
        printer(f"class {resource_class_name}(Resource):")
        with printer.indented():
            printer(f"interface = {self.class_name}")
            for opcode, event in enumerate(self.event):
                printer()
                event.output(printer, opcode, self.class_name, module_imports)

        printer()
        printer()
        printer(f"class {global_class_name}(Global):")
        with printer.indented():
            printer(f"interface = {self.class_name}")

        printer()
        printer()
        printer("{}._gen_c()".format(self.class_name))
        printer(f"{self.class_name}.proxy_class = {proxy_class_name}")
        printer(f"{self.class_name}.resource_class = {resource_class_name}")
        printer(f"{self.class_name}.global_class = {global_class_name}")
