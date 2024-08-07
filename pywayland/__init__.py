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

from .version import __version__  # noqa: F401

try:
    from ._ffi import ffi, lib  # noqa: F401
except ImportError:
    raise ImportError(
        "No module named pywayland._ffi, be sure to run `python ./pywayland/ffi_build.py`"
    )

__wayland_version__ = f"{lib.WAYLAND_VERSION_MAJOR}.{lib.WAYLAND_VERSION_MINOR}.{lib.WAYLAND_VERSION_MICRO}"
