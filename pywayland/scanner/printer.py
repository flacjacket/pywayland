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

import re

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

# Match function calls wl_inter_face.function and interface names wl_inter_face
re_doc = re.compile(r'(?P<iface>wl(?:_[a-z]+)+)(?P<func>\.[a-z]+(?:_[a-z]+)*)?')


class Printer(object):
    """Base level printer object

    Allows for storing of lines to be output from the definition of a
    protocol.  Lines are added by directly calling the printer object.
    """
    def __init__(self):
        self.level = 0
        self.lines = []
        self.iface_name = None

    def __call__(self, new_line=''):
        """Add the new line to the printer"""
        if new_line:
            self.lines.append(('    ' * self.level) + new_line)
        else:
            self.lines.append('')

    def doc(self, new_line):
        """Add lines as docstrings

        Performs additional massaging of strings, replacing references to other
        protocols and protocol methods with the appropriate Sphinx
        cross-reference.
        """
        new_line = re_doc.sub(self._doc_replace, new_line)
        self(new_line)

    def _get_iface(self, iface_name):
        iface_file = ''.join(iface_name.split('_')[1:])
        iface_class = ''.join(x.capitalize() for x in iface_name.split('_')[1:])

        if iface_name == self.iface_name:
            iface_path = iface_class
        else:
            iface_path = 'pywayland.protocol.{}.{}'.format(iface_file, iface_class)

        return iface_class, iface_path, iface_name != self.iface_name

    def _doc_replace(self, match):
        iface_name = match.group('iface')
        iface, iface_path, _ = self._get_iface(iface_name)

        func = match.group('func')
        if func:
            if iface_name == self.iface_name:
                return ':func:`{}{}`'.format(iface, func)
            else:
                return ':func:`{class_name}{func}() <{path}{func}>`'.format(class_name=iface, func=func, path=iface_path)
        else:
            if iface_name == self.iface_name:
                return ':class:`{}`'.format(iface)
            else:
                return ':class:`~{}`'.format(iface_path)

    def inc_level(self):
        """Increment the indent level"""
        self.level += 1

    def dec_level(self):
        """Decrement the indent level"""
        self.level -= 1

    def initialize_file(self, iface_name=None):
        """Initialize the file by writing out the copywrite"""
        self.iface_name = iface_name

        for line in copyright.split('\n'):
            self(line)

    def write(self, _file):
        """Write the lines added to the printer out to the given file"""
        for line in self.lines:
            _file.write(line)
            _file.write('\n')
