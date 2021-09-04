# Copyright 2015 Sean Vig
# Copyright 2021 Matt Colligan
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
from functools import wraps
from typing import Callable, Iterator, Optional

from . import ffi, lib


def ensure_valid(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._ptr is None:
            raise ValueError(
                "{cls} object has been destroyed".format(cls=self.__class__.__name__)
            )
        return func(self, *args, **kwargs)

    return wrapper


class AnonymousFile:
    """Anonymous file object

    Provides access to anonymous file objects that can be used by Wayland
    clients to render to surfaces.  Uses a method similar to Weston to open an
    anonymous file, so XDG_RUNTIME_DIR must be set for this to work properly.

    This class provides a content manager, that is, it can be used with Python
    ``with`` statements, where the value returned is the file descriptor.
    """

    def __init__(self, size: int) -> None:
        self.size = size
        self.fd: Optional[int] = None

    def __enter__(self) -> int:
        self.open()

        assert self.fd is not None
        return self.fd

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def open(self) -> None:
        """Open an anonymous file

        Opens the anonymous file and sets the ``fd`` property to the file
        descriptor that has been opened.
        """
        if self.fd is not None:
            raise IOError("File is already open")
        self.fd = lib.os_create_anonymous_file(self.size)
        if self.fd < 0:
            raise IOError("Unable to create anonymous file")

    def close(self) -> None:
        """Close the anonymous file

        Closes the file descriptor and sets the ``fd`` property to ``None``.
        Does nothing if the file is not open.
        """
        if self.fd is None:
            return

        os.close(self.fd)
        self.fd = None


def wl_container_of(ptr: ffi.CData, ctype: str, member: str, *, ffi=ffi) -> ffi.CData:
    """
    #define wl_container_of(ptr, sample, member)				\
            (__typeof__(sample))((char *)(ptr) -				\
                                 offsetof(__typeof__(*sample), member))

    :param ptr:
        Pointer to contained object
    :param ctype:
        ctype of container as string
    :param member:
        Member name of contained object in ctype
    :param ffi:
        ffi module to use. The default is pywayland, but this allows the use of this
        macro by other ffi modules that use `wl_list`s.
    """
    return ffi.cast(ctype, ffi.cast("char *", ptr) - ffi.offsetof(ctype, member))  # type: ignore[no-any-return]


def wl_list_for_each(
    ctype: str, head: ffi.CData, member: str, *, ffi=ffi
) -> Iterator[ffi.CData]:
    """
    #define wl_list_for_each(pos, head, member)				\
        for (pos = wl_container_of((head)->next, pos, member);	\
             &pos->member != (head);					\
             pos = wl_container_of(pos->member.next, pos, member))

    :param ctype:
        ctype of container as string
    :param head:
        The struct wl_list
    :param member:
        Member name of struct wl_list in ctype
    :param ffi:
        ffi module to use. The default is pywayland, but this allows the use of this
        macro by other ffi modules that use `wl_list`s.
    """
    pos = wl_container_of(head.next, ctype, member, ffi=ffi)

    while getattr(pos, member) != head:
        yield pos
        pos = wl_container_of(getattr(pos, member).next, ctype, member, ffi=ffi)
