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

import subprocess

from setuptools import setup

# For the purposes of uploading to PyPI, we'll get the version of Wayland here
with open("README.rst") as f:
    rst_input = f.read().strip().split("\n")
try:
    from pywayland import (
        __version__ as pywayland_version,
    )
    from pywayland import (
        __wayland_version__ as wayland_version,
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
            "    :target: https://github.com/flacjacket/pywayland/actions",
            "    :alt: Build Status",
            f".. |coveralls| image:: https://coveralls.io/repos/flacjacket/pywayland/badge.svg?branch={version_tag}",
            f"    :target: https://coveralls.io/github/flacjacket/pywayland?branch={version_tag}",
            "    :alt: Build Coverage",
            f".. |docs| image:: https://readthedocs.org/projects/pywayland/badge/?version={version_tag}",
            f"    :target: https://pywayland.readthedocs.io/en/{version_tag}/",
            "    :alt: Documentation Status",
        ]
    )

long_description = "\n".join(rst_input)

subprocess.run(["python", "-m", "pywayland.scanner", "--with-protocols"])
setup(
    long_description=long_description,
    long_description_content_type="text/x-rst",
    cffi_modules=["pywayland/ffi_build.py:ffi_builder"],
)
