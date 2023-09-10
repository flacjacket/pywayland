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

import xml.etree.ElementTree as ET
from dataclasses import dataclass

from .description import Description
from .element import Element
from .printer import Printer


@dataclass(frozen=True)
class Entry(Element):
    """Scanner for enum entries

    Required attributes: `name` and `value`

    Optional attributes: `summary` and `since`

    Child elements: `description`
    """

    name: str
    value: str
    summary: str | None
    since: str | None
    description: Description | None

    @classmethod
    def parse(cls, element: ET.Element) -> Entry:
        return Entry(
            name=cls.parse_attribute(element, "name"),
            value=cls.parse_attribute(element, "value"),
            summary=cls.parse_optional_attribute(element, "summary"),
            since=cls.parse_optional_attribute(element, "since"),
            description=cls.parse_optional_child(element, Description, "description"),
        )

    def output(self, enum_name: str, printer: Printer) -> None:
        """Generate the output for the entry in the enum"""
        # keep base 10 ints unchanged, but ensure that hexidecimal ints are
        # formatted 0xABC
        if self.value[:2] == "0x":
            value = f"0x{self.value[2:].upper()}"
        else:
            value = self.value

        try:
            int(self.name)
            printer(f"{enum_name}_{self.name} = {value}")
        except ValueError:
            if self.name in ("name", "async"):
                name = self.name + "_"
            else:
                name = self.name
            printer(f"{name} = {value}")
