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

from dataclasses import dataclass
from typing import Optional, Type, TYPE_CHECKING

from pywayland.scanner.argument import ArgumentType

if TYPE_CHECKING:
    from .interface import Interface  # noqa: F401


class classproperty:
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)


@dataclass(frozen=True)
class Argument:
    argument_type: ArgumentType
    nullable: bool = False
    interface: Optional[Type["Interface"]] = None

    @property
    def signature(self) -> str:
        if self.argument_type == ArgumentType.Int:
            base_signature = "i"
        elif self.argument_type == ArgumentType.Uint:
            base_signature = "u"
        elif self.argument_type == ArgumentType.Fixed:
            base_signature = "f"
        elif self.argument_type == ArgumentType.String:
            base_signature = "s"
        elif self.argument_type == ArgumentType.Object:
            base_signature = "o"
        elif self.argument_type == ArgumentType.NewId:
            if self.interface is None:
                base_signature = "sun"
            else:
                base_signature = "n"
        elif self.argument_type == ArgumentType.Array:
            base_signature = "a"
        elif self.argument_type == ArgumentType.FileDescriptor:
            base_signature = "h"

        if self.nullable:
            return "?" + base_signature
        return base_signature
