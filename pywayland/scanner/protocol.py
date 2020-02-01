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

import xml.etree.ElementTree as ET
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

from .element import Element
from .copyright import Copyright, copyright_default
from .description import Description
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
    copyright: Optional[Copyright]
    description: Optional[Description]
    interface: List[Interface]

    @classmethod
    def parse_file(cls, input_file: str) -> "Protocol":
        if not os.path.exists(input_file):
            raise ValueError("Input xml file does not exist: {}".format(input_file))
        xmlroot = ET.parse(input_file).getroot()
        if xmlroot.tag != "protocol":
            raise ValueError(
                "Input file not a valid Wayland protocol file: {}".format(input_file)
            )

        return cls.parse(xmlroot)

    @classmethod
    def parse(cls, element: ET.Element) -> "Protocol":
        return cls(
            name=cls.parse_attribute(element, "name"),
            copyright=cls.parse_optional_child(element, Copyright, "copyright"),
            description=cls.parse_optional_child(element, Description, "description"),
            interface=cls.parse_repeated_child(element, Interface, "interface"),
        )

    def __repr__(self) -> str:
        return "Protocol({})".format(self.name)

    def output(self, output_dir: str, module_imports: Dict[str, str]) -> None:
        """Output the scanned files to the given directory

        :param output_dir: Path of directory to output protocol files to
        :type output_dir: string
        """
        protocol_name = self.name.replace("-", "_")

        output_dir = os.path.join(output_dir, protocol_name)
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        # First, we'll create the __init__.py file
        printer = Printer(protocol_name)
        if self.copyright:
            self.copyright.output(printer)
        else:
            printer(copyright_default)

        printer()
        for iface in sorted(self.interface, key=lambda x: x.name):
            printer(
                "from .{} import {}  # noqa: F401".format(iface.name, iface.class_name)
            )

        init_path = os.path.join(output_dir, "__init__.py")
        with open(init_path, "wb") as f:
            printer.write(f)

        # Now build all the modules
        for iface in self.interface:
            module_path = os.path.join(output_dir, iface.name + ".py")

            printer = Printer(self.name.replace("-", "_"), iface.name, module_imports)
            if self.copyright:
                self.copyright.output(printer)
            else:
                printer(copyright_default)
            printer()

            iface.output(printer, module_imports)

            with open(module_path, "wb") as f:
                printer.write(f)
