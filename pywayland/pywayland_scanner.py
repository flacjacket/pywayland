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

from pywayland.scanner.scanner import Scanner

import argparse
import os

this_dir = os.path.split(__file__)[0]
protocol_dir = os.path.join(this_dir, 'protocol')

xml_file = '/usr/share/wayland/wayland.xml'


def main():
    parser = argparse.ArgumentParser(
        description='Generate wayland protocol files from xml'
    )
    parser.add_argument(
        '-i', '--input', metavar='XML_FILE', default=xml_file, type=str,
        help='Location of input xml file to scan'
    )
    parser.add_argument(
        '-o', '--output', metavar='DIR', default=protocol_dir, type=str,
        help='Location to output protocol files'
    )

    args = parser.parse_args()

    if not os.path.exists(args.output):
        os.makedirs(args.output, 0o775)

    scanner = Scanner(args.input)
    scanner.scan()
    scanner.output(args.output)


if __name__ == '__main__':
    main()
