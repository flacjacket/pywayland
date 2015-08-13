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

from .interface import Interface
from .printer import Printer

import xml.etree.ElementTree as ET
import os


class Scanner(object):
    """Main scanner object

    Main scanner object that acts on the input ``wayland.xml`` file to generate
    protocol files.

    Required attributes: `name`

    Child elements: `copywright` and `interface`

    :param input_file: Name of input XML file
    """
    def __init__(self, input_file):
        self._input_file = os.path.basename(input_file)
        if not os.path.exists(input_file):
            raise ValueError("Input xml file does not exist: {}".format(input_file))
        self._protocol = ET.parse(input_file).getroot()
        if self._protocol.tag != 'protocol':
            raise ValueError("Input file not a valid Wayland protocol file: {}".format(input_file))

        # attrib = self._protocol.attrib
        # if 'name' not in attrib or attrib['name'] != 'wayland':
        #     raise ValueError("Input file not a valid Wayland protocol file: {}".format(input_file))

    def __repr__(self):
        return "Scanner({})".format(self._input_file)

    def scan(self):
        """Scan the initialized xml file"""
        self.interfaces = [Interface(iface) for iface in self._protocol.findall('interface')]

        for iface in self.interfaces:
            iface.scan()

    def output(self, output_dir):
        """Output the scanned files to the given directory


        :param output_dir: Path of directory to output protocol files to
        :type output_dir: string
        """
        printer = Printer()
        printer.initialize_file()
        path = os.path.join(output_dir, '__init__.py')
        with open(path, 'w') as f:
            printer.write(f)
            f.write('\n')
            for iface in self.interfaces:
                f.write('from .{} import {}  # noqa'.format(iface.module, iface.class_name))
                f.write('\n')

        for iface in self.interfaces:
            path = os.path.join(output_dir, iface.file_name)

            printer = Printer()
            iface.output(printer)

            with open(path, 'w') as f:
                printer.write(f)
