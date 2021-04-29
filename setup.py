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
import subprocess
import sys

from setuptools import setup
from setuptools.command.install import install
from setuptools.command.sdist import sdist

try:
    from wheel.bdist_wheel import bdist_wheel
except ImportError:
    bdist_wheel = None

# we need this to import the version and scanner module directly so we can
# build the protocol before the cffi module has been compiled
sys.path.insert(0, "pywayland")

default_xml_file = "/usr/share/wayland/wayland.xml"


def get_protocol_command(klass):
    class ProtocolCommand(klass):
        user_options = [
            ("xml-file=", None, "Location of wayland.xml protocol file"),
            ("output-dir=", None, "Output location for protocol python files"),
            (
                "wayland-protocols",
                None,
                "Force generation of external protocols from wayland-protocols",
            ),
            (
                "no-wayland-protocols",
                None,
                "Disable generation of external protocols from wayland-protocols",
            ),
        ] + klass.user_options
        boolean_options = [
            "wayland-protocols",
            "no-wayland-protocols",
        ] + klass.boolean_options

        def initialize_options(self):
            from scanner.__main__ import pkgconfig

            # try to figure out where the main wayland protocols are installed
            try:
                data_dir = pkgconfig("wayland-scanner", "pkgdatadir")
            except subprocess.CalledProcessError:
                # silently fallback to the default
                self.xml_file = default_xml_file
            else:
                self.xml_file = os.path.join(data_dir, "wayland.xml")

            self.output_dir = "./pywayland/protocol"
            self.wayland_protocols = False
            self.no_wayland_protocols = False

            klass.initialize_options(self)

        def finalize_options(self):
            assert os.path.exists(self.xml_file), (
                "Specified Wayland protocol file, {}, does not exist "
                "please specify valid protocol file".format(self.xml_file)
            )

            klass.finalize_options(self)

        def run(self):
            from scanner import Protocol
            from scanner.__main__ import get_wayland_protocols

            # Generate the wayland interface by default
            input_files = [self.xml_file]

            # Unless users says don't build protocols, try to build them
            if not self.no_wayland_protocols:
                try:
                    protocol_files = get_wayland_protocols()
                    input_files += protocol_files
                except Exception:
                    # but only complain if we ask specifically to build them
                    if self.wayland_protocols:
                        raise

            # Ensure the output dir exists
            if not os.path.isdir(self.output_dir):
                os.makedirs(self.output_dir, 0o775)

            # Run and scan all the above found xml files
            protocols = [Protocol.parse_file(input_xml) for input_xml in input_files]
            protocol_imports = {
                interface.name: protocol.name
                for protocol in protocols
                for interface in protocol.interface
            }

            for protocol in protocols:
                protocol.output(self.output_dir, protocol_imports)

            self.distribution.packages.extend(
                f"pywayland.protocol.{protocol.name}" for protocol in protocols
            )

            klass.run(self)

    return ProtocolCommand


InstallCommand = get_protocol_command(install)
SdistCommand = get_protocol_command(sdist)

cmdclass = {
    "install": InstallCommand,
    "sdist": SdistCommand,
}

if bdist_wheel is not None:
    BdistWheelCommand = get_protocol_command(bdist_wheel)
    cmdclass["bdist_wheel"] = BdistWheelCommand

# For the purposes of uploading to PyPI, we'll get the version of Wayland here
with open("README.rst") as f:
    rst_input = f.read().strip().split("\n")
try:
    from pywayland import (
        __wayland_version__ as wayland_version,
        __version__ as pywayland_version,
    )

    version_tag = f"v{pywayland_version}"
except Exception:
    pass
else:
    version = f"Built against Wayland {wayland_version}\n"
    rst_input.insert(3, version)

    # replace all of the badges and links to point to the current version
    rst_input = rst_input[:-9]
    rst_input.extend(
        [
            f".. |ci| image:: https://github.com/flacjacket/pywayland/actions/workflows/ci.yml/badge.svg?branch={version_tag}",
            f"    :target: https://github.com/flacjacket/pywayland/actions",
            f"    :alt: Build Status",
            f".. |coveralls| image:: https://coveralls.io/repos/flacjacket/pywayland/badge.svg?branch={version_tag}",
            f"    :target: https://coveralls.io/github/flacjacket/pywayland?branch={version_tag}",
            f"    :alt: Build Coverage",
            f".. |docs| image:: https://readthedocs.org/projects/pywayland/badge/?version={version_tag}",
            f"    :target: https://pywayland.readthedocs.io/en/{version_tag}/",
            f"    :alt: Documentation Status",
        ]
    )

long_description = "\n".join(rst_input)

setup(
    long_description=long_description,
    long_description_content_type="text/x-rst",
    cmdclass=cmdclass,
    cffi_modules=["pywayland/ffi_build.py:ffi_builder"],
)
