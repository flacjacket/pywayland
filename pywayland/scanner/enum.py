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

from dataclasses import dataclass
from typing import List, Optional
import xml.etree.ElementTree as ET

from .description import Description
from .entry import Entry
from .element import Element
from .printer import Printer


@dataclass(frozen=True)
class Enum(Element):
    """Scanner for enum objects

    Required attributes: `name` and `since`

    Child elements: `description` and `entry`
    """

    name: str
    since: Optional[str]
    is_bitfield: bool
    description: Optional[Description]
    entry: List[Entry]

    @classmethod
    def parse(cls, element: ET.Element) -> "Enum":
        is_bitfield = cls.parse_optional_attribute(element, "bitfield") == "true"
        return Enum(
            name=cls.parse_attribute(element, "name"),
            since=cls.parse_optional_attribute(element, "since"),
            is_bitfield=is_bitfield,
            description=cls.parse_optional_child(element, Description, "description"),
            entry=cls.parse_repeated_child(element, Entry, "entry"),
        )

    def output(self, printer: Printer) -> None:
        """Generate the output for the enum to the printer"""
        name = self.name if self.name != "version" else "version_"
        if self.is_bitfield:
            printer("class {0}(enum.IntFlag):".format(name))
        else:
            printer("class {0}(enum.IntEnum):".format(name))
        with printer.indented():
            for entry in self.entry:
                entry.output(self.name, printer)
