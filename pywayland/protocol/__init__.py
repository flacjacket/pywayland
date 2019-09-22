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

import enum
import sys


# there is not intflag in python 3.5, which is used in bitfield's
# without a proper flag type, these enums will be less usable, if we need to
# support this, we can pull in some backport of the necessary functionality
if sys.version_info < (3, 6):
    enum.IntFlag = enum.IntEnum
