# Copyright 2021 Sean Vig
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

import pytest

from pywayland.utils import AnonymousFile


def test_anonymous_file():
    with AnonymousFile(10) as fd:
        assert fd > 0

    f = AnonymousFile(10)
    f.close()

    f.open()
    with pytest.raises(IOError, match="File is already open"):
        f.open()
    f.close()
    f.close()
