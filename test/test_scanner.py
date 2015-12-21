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

import os
import pytest
import shutil
import tempfile

this_dir = os.path.split(__file__)[0]
scanner_dir = os.path.join(this_dir, 'scanner_files')
input_file = os.path.join(scanner_dir, 'test_scanner_input.xml')

pass_iface = ["__init__.py", "core.py", "events.py", "requests.py", "destructor.py"]
xfail_iface = ["xfail.py"]

generated_files = pass_iface + xfail_iface


def check_interface(iface_name, gen_lines):
    # Get output to check against
    check = os.path.join(scanner_dir, iface_name)
    with open(check, 'r') as f:
        check_lines = [line.strip('\n') for line in f.readlines()]

    # Run through both files, checking each line
    for gen_line, check_line in zip(gen_lines, check_lines):
        assert gen_line == check_line

    # Should both be the same length
    assert len(gen_lines) == len(check_lines)


def test_scanner():
    scanner = Scanner(input_file)

    output_dir = tempfile.mkdtemp()
    try:
        scanner.output(output_dir)
        test_dir = os.path.join(output_dir, "scanner_test")
        assert os.path.exists(test_dir)
        assert set(os.listdir(test_dir)) == set(generated_files)

        for interface in pass_iface:
            # Read in the generated file
            gen = os.path.join(test_dir, interface)
            with open(gen, 'r') as f:
                gen_lines = [line.strip('\n') for line in f.readlines()]
            # Pass it to the yielded test
            yield check_interface, interface, gen_lines

        for interface in xfail_iface:
            gen = os.path.join(test_dir, interface)
            with open(gen, 'r') as f:
                gen_lines = [line.strip('\n') for line in f.readlines()]
            yield pytest.mark.xfail(check_interface), interface, gen_lines
    finally:
        shutil.rmtree(output_dir)
