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

import os
import tempfile

import pytest

from pywayland.scanner import Protocol

this_dir = os.path.split(__file__)[0]
scanner_dir = os.path.join(this_dir, "scanner_files")
input_file = os.path.join(scanner_dir, "scanner-test-v1.xml")

protocol_tests = ["scanner_test_v1.py"]


@pytest.fixture(scope="session")
def protocol_directory():
    protocol = Protocol.parse_file(input_file)

    imports = {interface.name: protocol.name for interface in protocol.interface}

    test_files = [
        file if isinstance(file, str) else file.values[0] for file in protocol_tests
    ]

    with tempfile.TemporaryDirectory() as output_dir:
        protocol.output(output_dir, imports)

        assert os.path.exists(output_dir)
        assert set(os.listdir(output_dir)) == set(test_files)

        yield output_dir


@pytest.mark.parametrize("protocol_name", protocol_tests)
def test_protocol(protocol_directory, protocol_name):
    # Get the generated file output
    generated_file = os.path.join(protocol_directory, protocol_name)
    with open(generated_file) as f:
        gen_lines = [line.strip("\n") for line in f.readlines()]

    # Get output to check against
    check_file = os.path.join(scanner_dir, protocol_name)
    with open(check_file) as f:
        check_lines = [line.strip("\n") for line in f.readlines()]

    # Run through both files, checking each line
    for gen_line, check_line in zip(gen_lines, check_lines):
        assert gen_line == check_line

    # Should both be the same length
    assert len(gen_lines) == len(check_lines)
