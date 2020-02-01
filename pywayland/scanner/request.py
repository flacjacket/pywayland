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
from typing import Iterable, Optional
import xml.etree.ElementTree as ET

from .argument import Argument, ArgumentType
from .description import Description
from .method import Method
from .printer import Printer

# For 'new_id' types with no 'interface'
NO_IFACE = "interface"
NO_IFACE_VERSION = "version"


@dataclass(frozen=True)
class Request(Method):
    """Scanner for request objects (client-side method)

    Required attributes: `name`

    Optional attributes: `type` and `since`

    Child elements: `description` and `arg`
    """

    method_type = "request"

    type: Optional[str]

    @classmethod
    def parse(cls, element: ET.Element) -> "Request":
        name = cls.parse_attribute(element, "name")
        if name in ("global", "import"):
            name += "_"

        return cls(
            name=name,
            since=cls.parse_optional_attribute(element, "since"),
            description=cls.parse_optional_child(element, Description, "description"),
            arg=cls.parse_repeated_child(element, Argument, "arg"),
            type=cls.parse_optional_attribute(element, "type"),
        )

    @property
    def new_id(self) -> Optional[Argument]:
        for arg in self.arg:
            if arg.type == ArgumentType.NewId:
                return arg
        return None

    @property
    def method_args(self) -> Iterable[str]:
        """Generator of the arguments to the method

        The `new_id` args are generated in marshaling the args, they do not
        appear in the args of the method.
        """
        for arg in self.arg:
            if arg.type == ArgumentType.NewId:
                # An interface of known type is created for us
                if arg.interface:
                    continue
                # A `new_id` with no interface, c.f. wl_registry_bind
                # Need a string (interface name) and int (interface version)
                yield NO_IFACE
                yield NO_IFACE_VERSION
            else:
                yield arg.name

    @property
    def marshal_args(self) -> Iterable[str]:
        """Arguments sent to `._marshal`"""
        for arg in self.arg:
            if arg.type == ArgumentType.NewId:
                if not arg.interface:
                    yield "{}.name".format(NO_IFACE)
                    yield NO_IFACE_VERSION
            else:
                yield arg.name

    def output_doc_params(self, printer: Printer) -> None:
        """Aguments documented as parameters

        Anything that is not a `new_id` is
        """
        ret = None
        for arg in self.arg:
            if arg.type == ArgumentType.NewId:
                ret = arg
                if arg.interface:
                    continue
                printer(f":param {NO_IFACE}:")
                printer("    Interface name")
                printer(f":type {NO_IFACE}:")
                printer("    `string`")
                printer(f":param {NO_IFACE_VERSION}:")
                printer("    Interface version")
                printer(f":type {NO_IFACE_VERSION}:")
                printer("    `int`")
            else:
                arg.output_doc_param(printer)
        if ret is not None:
            ret.output_doc_ret(printer)

    def output_doc_ret(self, printer: Printer) -> None:
        """Aguments documented as return values

        Arguments of type `new_id` are returned from requests.
        """
        for arg in self.arg:
            if arg.type == ArgumentType.NewId:
                arg.output_doc_ret(printer)

    def output_body(self, printer: Printer, opcode: int) -> None:
        """Output the body of the request to the printer"""
        if self.new_id:
            if self.new_id.interface:
                id_class = self.new_id.interface_class
            else:
                id_class = NO_IFACE
            args = ", ".join([str(opcode), id_class] + list(self.marshal_args))
            printer("{} = self._marshal_constructor({})".format(self.new_id.name, args))
            printer("return {}".format(self.new_id.name))
        else:
            args = ", ".join([str(opcode)] + list(self.marshal_args))
            printer("self._marshal({})".format(args))
            if self.type == "destructor":
                printer("self._destroy()")
