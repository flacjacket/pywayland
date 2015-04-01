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

from .ffi import ffi, C  # noqa

__version__ = '0.0.1a.dev1'
__wayland_version__ = '{:d}.{:d}.{:d}'.format(
    C.WAYLAND_VERSION_MAJOR,
    C.WAYLAND_VERSION_MINOR,
    C.WAYLAND_VERSION_MICRO
)
