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

from pywayland.scanner.printer import Printer
from pywayland.scanner.scanner import Scanner

import os
import pytest
import shutil
import tempfile

this_dir = os.path.split(__file__)[0]
scanner_dir = os.path.join(this_dir, 'scanner_files')
input_file = os.path.join(scanner_dir, 'test_scanner_input.xml')

generated_files = [
    "core.py", "destructor.py", "events.py", "requests.py", "xfail.py",
    "__init__.py"
]

pass_iface = ["core.py", "events.py", "requests.py", "destructor.py"]
xfail_iface = ["xfail.py"]

generated_files = ["__init__.py"] + pass_iface + xfail_iface


def check_interface(scanner, iface_name):
    # First, we need to get the interface out
    for iface in scanner.interfaces:
        if iface.file_name == iface_name:
            break
    else:
        raise ValueError("Scanner has no interface: {}".format(iface_name))

    # Pull the output of interface
    printer = Printer()
    iface.output(printer)
    lines = printer.lines

    # Get output to check against
    check = os.path.join(scanner_dir, iface_name)
    with open(check, 'r') as f:
        check_lines = [line.strip('\n') for line in f.readlines()]

    # Run through both files, checking each line
    for line, check in zip(lines, check_lines):
        assert line == check

    # Should both be the same length
    assert len(lines) == len(check_lines)


def test_scanner():
    scanner = Scanner(input_file)
    scanner.scan()

    output_dir = tempfile.mkdtemp()
    try:
        scanner.output(output_dir)
        assert set(os.listdir(output_dir)) == set(generated_files)

        for interface in pass_iface:
            yield check_interface, scanner, interface

        for interface in xfail_iface:
            yield pytest.mark.xfail(check_interface), scanner, interface
    finally:
        shutil.rmtree(output_dir)
