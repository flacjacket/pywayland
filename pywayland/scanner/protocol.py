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

import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass

from .copyright import Copyright, copyright_default
from .description import Description
from .element import Element
from .interface import Interface
from .printer import Printer


@dataclass(frozen=True)
class Protocol(Element):
    """Protocol scanner object

    Main scanner object that acts on the input xml files to generate protocol
    files.

    Required attributes: `name`

    Child elements: `copyright?`, `description?`, and `interface+`

    :param input_file: Name of input XML file
    """

    name: str
    copyright: Copyright | None
    description: Description | None
    interface: list[Interface]

    @classmethod
    def parse_file(cls, input_file: str) -> Protocol:
        if not os.path.exists(input_file):
            raise ValueError(f"Input xml file does not exist: {input_file}")
        xmlroot = ET.parse(input_file).getroot()
        if xmlroot.tag != "protocol":
            raise ValueError(
                f"Input file not a valid Wayland protocol file: {input_file}"
            )

        return cls.parse(xmlroot)

    @classmethod
    def parse(cls, element: ET.Element) -> Protocol:
        return cls(
            name=cls.parse_attribute(element, "name"),
            copyright=cls.parse_optional_child(element, Copyright, "copyright"),
            description=cls.parse_optional_child(element, Description, "description"),
            interface=cls.parse_repeated_child(element, Interface, "interface"),
        )

    def __repr__(self) -> str:
        return f"Protocol({self.name})"

    def output(self, output_dir: str, all_imports: dict[str, str]) -> None:
        """Output the scanned files to the given directory

        :param output_dir: Path of directory to output protocol files to
        :type output_dir: string
        """
        protocol_name = self.name.replace("-", "_")

        output_dir = os.path.join(output_dir, protocol_name)
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        init_path = os.path.join(output_dir, "__init__.py")

        printer = Printer(protocol_name, all_imports)
        if self.copyright:
            self.copyright.output(printer)
        else:
            printer(copyright_default)
        printer()

        printer("from __future__ import annotations")
        printer()

        if any([iface.enum for iface in self.interface]):
            printer("import enum")
            printer()

        typing_imports = []
        if any([iface.needs_any_type for iface in self.interface]):
            typing_imports.extend(["Any"])

        pywayland_imports = []
        if any([iface.needs_t_type for iface in self.interface]):
            typing_imports.extend(["TypeVar"])

        if typing_imports:
            printer(f"from typing import {', '.join(sorted(typing_imports))}")
            printer()

        if any([iface.needs_argument_type for iface in self.interface]):
            pywayland_imports.extend(["Argument", "ArgumentType"])

        pywayland_imports.extend(["Interface", "Global", "Proxy", "Resource"])
        printer(
            f"from pywayland.protocol_core import {(', ').join(sorted(pywayland_imports))}"
        )
        printer()

        interface_imports = set()  # type: ignore
        for iface in self.interface:
            interface_imports |= iface.get_imports(all_imports)

        for module, import_ in sorted(interface_imports):
            printer(f"from {module} import {import_}")
        if interface_imports:
            printer()

        if "TypeVar" in typing_imports:
            printer('T = TypeVar("T", bound=Interface)')
            printer()

        with open(init_path, "wb") as f:
            printer.write(f)
        printer.clear()

        output_methods = [
            "output_interface",
            "output_events",
            "output_requests",
            "output_global",
        ]

        for output_method in output_methods:
            for iface in sorted(self.interface):
                printer.interface_name = iface.name
                iface_method = getattr(iface, output_method)
                iface_method(printer)

            with open(init_path, "ab") as f:
                printer.write(f)
            printer.clear()
