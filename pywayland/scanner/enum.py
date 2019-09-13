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

from .description import Description
from .entry import Entry
from .element import Element, Attribute, Child


class Enum(Element):
    """Scanner for enum objects

    Required attributes: `name` and `since`

    Child elements: `description` and `entry`
    """

    attributes = [
        Attribute('name', True),
        Attribute('since', False),
        Attribute('bitfield', False)
    ]

    children = [
        Child('description', Description, False, False),
        Child('entry', Entry, False, True)
    ]

    def output(self, printer):
        """Generate the output for the enum to the printer"""
        name = self.name if self.name != "version" else "version_"
        printer('{0} = enum.Enum("{0}", {{'.format(name))
        with printer.indented():
            for entry in self.entry:
                entry.output(printer)
        printer('})')
