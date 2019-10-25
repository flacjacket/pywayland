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

from pywayland.scanner import Protocol

import os
import pytest
import tempfile

this_dir = os.path.split(__file__)[0]
scanner_dir = os.path.join(this_dir, 'scanner_files')
input_file = os.path.join(scanner_dir, 'test_scanner_input.xml')

interface_tests = [
    "__init__.py",
    "wl_core.py",
    "wl_events.py",
    "wl_requests.py",
    "wl_destructor.py",
    pytest.param("wl_xfail.py", marks=pytest.mark.xfail),
]


@pytest.fixture(scope="session")
def protocol_directory():
    scanner = Protocol.parse_file(input_file)

    imports = {
        interface.name: scanner.name
        for interface in scanner.interface
    }

    generated_files = [
        iface if isinstance(iface, str) else iface.values[0]
        for iface in interface_tests
    ]

    with tempfile.TemporaryDirectory() as output_dir:
        scanner.output(output_dir, imports)

        test_dir = os.path.join(output_dir, "scanner_test")
        assert os.path.exists(test_dir)
        assert set(os.listdir(test_dir)) == set(generated_files)

        yield test_dir


@pytest.mark.parametrize("iface_name", interface_tests)
def test_interface(protocol_directory, iface_name):
    # Get the generated file output
    generated_file = os.path.join(protocol_directory, iface_name)
    with open(generated_file) as f:
        gen_lines = [line.strip('\n') for line in f.readlines()]

    # Get output to check against
    check_file = os.path.join(scanner_dir, iface_name)
    with open(check_file) as f:
        check_lines = [line.strip('\n') for line in f.readlines()]

    # Run through both files, checking each line
    for gen_line, check_line in zip(gen_lines, check_lines):
        assert gen_line == check_line

    # Should both be the same length
    assert len(gen_lines) == len(check_lines)
