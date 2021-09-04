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

import argparse
import logging
import os
import shlex
import subprocess
from typing import List

from .protocol import Protocol

logger = logging.getLogger(__name__)


def pkgconfig(package, variable) -> str:
    """pkg-config"""
    pkgconfig_env = os.environ.get("PKG_CONFIG", "pkg-config")
    cmd = f"{pkgconfig_env} --variable={variable} {package}"
    args = shlex.split(cmd)
    return subprocess.check_output(args).decode().strip()


def get_wayland_protocols() -> List[str]:
    # use pkg-config to try to find the wayland-protocol directory
    try:
        protocols_dir = pkgconfig("wayland-protocols", "pkgdatadir")
    except subprocess.CalledProcessError:
        raise OSError("Unable to find wayland-protocols using pkgconfig")

    protocols = []
    # walk the wayland-protocol dir
    for dirpath, _, filenames in os.walk(protocols_dir):
        for filename in filenames:
            file_base, file_ext = os.path.splitext(filename)
            # only generate protocols for xml files
            if file_ext == ".xml":
                protocols.append(os.path.join(dirpath, filename))

    # this is pretty brittle, there is an xdg_popup in both the unstable and
    # stable xdg_shell implementations. process the unstable version first so
    # the import is correct when the pop-up tries to import other interfaces.
    return sorted(protocols, reverse=True)


def main() -> None:
    this_dir = os.path.split(__file__)[0]
    protocol_dir = os.path.join(this_dir, "..", "protocol")

    # try to figure out where the wayland.xml file is installed, otherwise use
    # default
    try:
        xml_dir = pkgconfig("wayland-scanner", "pkgdatadir")
        xml_file = os.path.join(xml_dir, "wayland.xml")
    except subprocess.CalledProcessError:
        xml_file = "/usr/share/wayland/wayland.xml"

    parser = argparse.ArgumentParser(
        description="Generate wayland protocol files from xml"
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        metavar="DIR",
        default=protocol_dir,
        type=str,
        help="Directory to output protocol files",
    )
    parser.add_argument(
        "--with-protocols",
        action="store_true",
        help="Also locate and build wayland-protocol xml files (using pkg-config)",
    )
    parser.add_argument(
        "-i",
        "--input",
        metavar="XML_FILE",
        default=[xml_file],
        nargs="+",
        type=str,
        help="Path to input xml file to scan",
    )

    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir, 0o775)

    input_files = args.input

    if args.with_protocols:
        protocols_files = get_wayland_protocols()
        input_files += protocols_files

    protocols = [Protocol.parse_file(input_file) for input_file in input_files]
    logger.info("Parsed {} input xml files".format(len(protocols)))

    protocol_imports = {
        interface.name: protocol.name
        for protocol in protocols
        for interface in protocol.interface
    }

    for protocol in protocols:
        protocol.output(args.output_dir, protocol_imports)
        logger.info("Generated protocol: {}".format(protocol.name))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
