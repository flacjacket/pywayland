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

from __future__ import annotations

import itertools
import xml.etree.ElementTree as ET
from dataclasses import dataclass

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
    description: Description | None
    enum: list[Enum]
    event: list[Event]
    request: list[Request]

    def __lt__(self, other):
        return self.name < other.name

    @classmethod
    def parse(cls, element: ET.Element) -> Interface:
        """Scanner for interface objects

        Required attributes: `name` and `version`

        Child elements: `description`, `request`, `event`, `enum`
        """
        return cls(
            name=cls.parse_attribute(element, "name"),
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

    @property
    def needs_t_type(self) -> bool:
        return any(req.new_id and not req.new_id.interface for req in self.request)

    @property
    def needs_any_type(self) -> bool:
        return any(req.needs_any for req in self.request) or any(
            event.needs_any for event in self.event
        )

    @property
    def needs_argument_type(self) -> bool:
        return any(len(method.arg) > 0 for method in self.request) or any(
            len(method.arg) > 0 for method in self.event
        )

    def get_imports(self, all_imports: dict[str, str]) -> set:
        """Return necessary imports for this interface"""
        return set(
            _import
            for method in itertools.chain(self.request, self.event)
            for _import in method.imports(self.name, all_imports)
        )

    def output_interface(self, printer: Printer) -> None:
        """Generate the output only of the interface class"""
        printer()
        printer()
        # Class definition
        printer(f"class {self.class_name}(Interface):")
        with printer.indented():
            # Docstring
            if self.description:
                self.description.output(printer)
                printer('"""')
                printer()
            # Class attributes
            printer(f'name = "{self.name}"')
            printer(f"version = {self.version}")
            # Enums
            for enum in self.enum:
                printer()
                enum.output(printer)

    def output_requests(self, printer: Printer) -> None:
        """Generate the output only of the proxy class"""
        printer()
        printer()
        proxy_class_name = f"{self.class_name}Proxy"
        printer(f"class {proxy_class_name}(Proxy[{self.class_name}]):")
        with printer.indented():
            printer(f"interface = {self.class_name}")
            for opcode, request in enumerate(self.request):
                printer()
                request.output(printer, opcode, self.class_name)
        printer()
        printer()
        printer(f"{self.class_name}.proxy_class = {proxy_class_name}")

    def output_events(self, printer: Printer) -> None:
        """Generate the output only of the proxy class"""
        printer()
        printer()
        resource_class_name = f"{self.class_name}Resource"
        printer(f"class {resource_class_name}(Resource):")
        with printer.indented():
            printer(f"interface = {self.class_name}")
            for opcode, event in enumerate(self.event):
                printer()
                event.output(printer, opcode, self.class_name)
        printer()
        printer()
        printer(f"{self.class_name}.resource_class = {resource_class_name}")

    def output_global(self, printer: Printer) -> None:
        """Generate the output only of the proxy class"""
        printer()
        printer()
        global_class_name = f"{self.class_name}Global"
        printer(f"class {global_class_name}(Global):")
        with printer.indented():
            printer(f"interface = {self.class_name}")
        printer()
        printer()
        printer(f"{self.class_name}.global_class = {global_class_name}")

        printer()
        printer()
        printer(f"{self.class_name}._gen_c()")
