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

from .description import Description
from .entry import Entry
from .element import Element
from .printer import Printer


class Enum(Element):
    """Scanner for enum objects

    Required attributes: `name` and `since`

    Child elements: `description` and `entry`
    """

    def __init__(self, element: ET.Element) -> None:
        self.name = self.parse_attribute(element, "name")
        self.since = self.parse_optional_attribute(element, "since")
        self.bitfield = self.parse_optional_attribute(element, "bitfield")

        self.description = self.parse_optional_child(element, Description, "description")
        self.entry = self.parse_repeated_child(element, Entry, "entry")

    def output(self, printer: Printer) -> None:
        """Generate the output for the enum to the printer"""
        name = self.name if self.name != "version" else "version_"
        if self.bitfield:
            printer('class {0}(enum.IntFlag):'.format(name))
        else:
            printer('class {0}(enum.IntEnum):'.format(name))
        with printer.indented():
            for entry in self.entry:
                entry.output(self.name, printer)
