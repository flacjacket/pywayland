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

copyright = """\
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
# limitations under the License."""


class Printer(object):
    def __init__(self):
        """Base level printer object

        Allows for storing of lines to be output from the definition of a
        protocol.  Lines are added by directly calling the printer object.
        """
        self.level = 0
        self.lines = []

    def __call__(self, new_line=''):
        """Add the new line to the printer"""
        if new_line:
            self.lines.append(('    ' * self.level) + new_line)
        else:
            self.lines.append('')

    def inc_level(self):
        """Increment the indent level"""
        self.level += 1

    def dec_level(self):
        """Decrement the indent level"""
        self.level -= 1

    def initialize_file(self):
        """Initialize the file by writing out the copywrite"""
        for line in copyright.split('\n'):
            self(line)

    def write(self, _file):
        """Write the lines added to the printer out to the given file"""
        for line in self.lines:
            _file.write(line)
            _file.write('\n')
