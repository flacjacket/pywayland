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

from __future__ import absolute_import

try:
    from ._ffi import ffi, lib  # noqa
except ImportError:
    # PyPy < 2.6 compatibility
    from .ffi_build import ffi, SOURCE
    lib = ffi.verify(SOURCE, libraries=['wayland-client', 'wayland-server'])

__version__ = '0.0.1a.dev4'
__wayland_version__ = '{}.{}.{}'.format(
    lib.WAYLAND_VERSION_MAJOR,
    lib.WAYLAND_VERSION_MINOR,
    lib.WAYLAND_VERSION_MICRO
)
