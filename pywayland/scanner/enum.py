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

from .entry import Entry


class Enum(object):
    """Scanner for enum objects

    Required attributes: `name` and `since`

    Child elements: `description` and `entry`
    """
    def __init__(self, enum):
        self._enum = enum
        self.name = enum.attrib['name']

        self.since = enum.attrib['since'] if 'since' in enum.attrib else None

    def scan(self):
        """Scan the enum"""
        description = self._enum.find('description')
        if description:
            self.summary = description.attrib['summary']
            if description.text:
                self.description = description.text.strip()
            else:
                self.description = None
        else:
            self.summary = None
            self.description = None

        self.entries = [Entry(entry) for entry in self._enum.findall('entry')]

        for entry in self.entries:
            entry.scan()

    def output(self, printer):
        """Generate the output for the enum to the printer"""
        printer('{0} = enum.Enum("{0}", {{'.format(self.name))
        printer.inc_level()
        for entry in self.entries:
            entry.output(printer)
        printer.dec_level()
        printer('})')
