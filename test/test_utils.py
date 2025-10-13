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

from pywayland import ffi, lib
from pywayland.utils import (
    AnonymousFile,
    ensure_valid,
    wl_container_of,
    wl_list_for_each,
)


def test_ensure_valid_decorator_valid():
    class Dummy:
        def __init__(self):
            self._ptr = 1

        @ensure_valid
        def foo(self):
            return "ok"

    d = Dummy()
    assert d.foo() == "ok"


def test_ensure_valid_decorator_invalid():
    class Dummy:
        def __init__(self):
            self._ptr = None

        @ensure_valid
        def foo(self):
            return "fail"

    d = Dummy()
    with pytest.raises(ValueError):
        d.foo()


def test_anonymous_file_open_close():
    af = AnonymousFile(10)
    assert af.fd is None
    af.open()
    assert af.fd is not None
    af.close()
    assert af.fd is None


def test_anonymous_file_context_manager():
    af = AnonymousFile(10)
    with af as fd:
        assert af.fd == fd
        assert af.fd is not None
    assert af.fd is None


def test_anonymous_file_open_twice():
    af = AnonymousFile(10)
    af.open()
    with pytest.raises(OSError, match="File is already open"):
        af.open()
    af.close()


def test_anonymous_file_close_not_open():
    af = AnonymousFile(10)
    af.close()


def test_wl_container_of():
    ctype = "struct wl_listener *"
    member = "link"
    container = ffi.new(ctype)
    member_ptr = ffi.addressof(container[0], member)
    recovered = wl_container_of(member_ptr, ctype, member)
    assert recovered == container


def test_wl_list_for_each():
    ctype = "struct wl_listener *"
    member = "link"
    list_ptr = ffi.new("struct wl_list *")
    elem1 = ffi.new(ctype)
    elem1_list_ptr = ffi.addressof(elem1, member)
    elem2 = ffi.new(ctype)
    elem2_list_ptr = ffi.addressof(elem2, member)
    elem3 = ffi.new(ctype)
    elem3_list_ptr = ffi.addressof(elem3, member)
    lib.wl_list_init(list_ptr)
    lib.wl_list_insert(list_ptr, elem1_list_ptr)  # e1 is the first element
    lib.wl_list_insert(list_ptr, elem2_list_ptr)  # e2 is now the first element
    lib.wl_list_insert(elem2_list_ptr, elem3_list_ptr)  # insert e3 after e2
    result = list(wl_list_for_each(ctype, list_ptr, member))
    assert result == [elem2, elem3, elem1]
