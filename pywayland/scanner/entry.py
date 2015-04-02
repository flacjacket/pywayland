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


class Entry(object):
    """Scanner for enum entries

    Required attributes: `name` and `value`

    Optional attributes: `summary` and `since`

    Child elements: `description`
    """
    def __init__(self, entry):
        self._entry = entry
        self.name = entry.attrib['name']
        self.value = entry.attrib['value']

        self.summary = entry.attrib['since'] if 'since' in entry.attrib else None
        self.since = entry.attrib['since'] if 'since' in entry.attrib else None

    def scan(self):
        """Scan the enum entry"""
        # Currently no entries implement a description, instead, they have a
        # summary element
        pass

    def output(self, printer):
        """Generate the output for the entry in the enum"""
        printer('"{}": {},'.format(self.name, self.value))
