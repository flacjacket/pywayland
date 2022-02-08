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

from __future__ import annotations

from dataclasses import dataclass
import enum
import xml.etree.ElementTree as ET

from .description import Description
from .element import Element
from .printer import Printer

NO_IFACE_NAME = "interface"


@enum.unique
class ArgumentType(enum.Enum):
    Int = enum.auto()
    Uint = enum.auto()
    Fixed = enum.auto()
    String = enum.auto()
    Object = enum.auto()
    NewId = enum.auto()
    Array = enum.auto()
    FileDescriptor = enum.auto()


@dataclass(frozen=True)
class Argument(Element):
    """Argument to a request or event method

    Required attributes: `name` and `type`

    Optional attributes: `summary`, `interface`, and `allow-null`

    Child elements: `description`
    """

    name: str
    type: ArgumentType
    summary: str | None
    interface: str | None
    allow_null: bool
    enum: str | None
    description: Description | None

    @classmethod
    def parse(cls, element: ET.Element) -> Argument:
        arg_type_str = cls.parse_attribute(element, "type")
        if arg_type_str == "int":
            argument_type = ArgumentType.Int
        elif arg_type_str == "uint":
            argument_type = ArgumentType.Uint
        elif arg_type_str == "fixed":
            argument_type = ArgumentType.Fixed
        elif arg_type_str == "string":
            argument_type = ArgumentType.String
        elif arg_type_str == "object":
            argument_type = ArgumentType.Object
        elif arg_type_str == "new_id":
            argument_type = ArgumentType.NewId
        elif arg_type_str == "array":
            argument_type = ArgumentType.Array
        elif arg_type_str == "fd":
            argument_type = ArgumentType.FileDescriptor
        else:
            raise ValueError(f"Invalid argument type: {argument_type}")

        allow_null = cls.parse_optional_attribute(element, "allow-null") == "true"
        return cls(
            name=cls.parse_attribute(element, "name"),
            type=argument_type,
            summary=cls.parse_optional_attribute(element, "summary"),
            interface=cls.parse_optional_attribute(element, "interface"),
            allow_null=allow_null,
            enum=cls.parse_optional_attribute(element, "enum"),
            description=cls.parse_optional_child(element, Description, "description"),
        )

    @property
    def interface_class(self) -> str:
        """Returns the Interface class name

        Gives the class name for the Interface coresponding to the type of the
        argument.
        """
        assert self.interface is not None
        return "".join(x.capitalize() for x in self.interface.split("_"))

    @property
    def signature(self) -> str:
        """Output as the argument appears in the signature."""
        return f"{self.name}: {self._annotation}"

    @property
    def _annotation(self) -> str:
        """The type annotation for the argument."""
        if self.type == ArgumentType.Int:
            base_annotation = "int"
        elif self.type == ArgumentType.Uint:
            base_annotation = "int"
        elif self.type == ArgumentType.Fixed:
            base_annotation = "float"
        elif self.type == ArgumentType.String:
            base_annotation = "str"
        elif self.type == ArgumentType.Object:
            if self.interface:
                base_annotation = self.interface_class
            else:
                base_annotation = "Any"
        elif self.type == ArgumentType.NewId:
            if self.interface:
                base_annotation = self.interface_class
            else:
                base_annotation = "Any"
        elif self.type == ArgumentType.Array:
            base_annotation = "list"
        elif self.type == ArgumentType.FileDescriptor:
            base_annotation = "int"

        if self.allow_null:
            return f"{base_annotation} | None"
        return base_annotation

    @property
    def argument(self) -> str:
        """Output as an Argument"""
        args = [f"ArgumentType.{self.type.name}"]
        if self.interface is not None:
            args.append(f"interface={self.interface_class}")
        if self.allow_null:
            args.append("nullable=True")

        return f"Argument({', '.join(args)})"

    def output_doc_param(self, printer: Printer) -> None:
        """Document the argument as a parameter"""
        # Output the parameter and summary
        printer.doc(":param {}:".format(self.name))
        if self.summary:
            with printer.indented():
                printer.docstring(self.summary)

        # Determine the type to be output
        if self.interface:
            arg_type = self.interface
        else:
            arg_type = "`{}`".format(self.type)

        # Output the parameter type
        printer.doc(f":type {self.name}:")
        with printer.indented():
            if self.allow_null:
                printer.doc(f"{arg_type} or `None`")
            else:
                printer.doc(f"{arg_type}")

    def output_doc_ret(self, printer: Printer) -> None:
        """Document the argument as a return"""
        # Determine the type to be output
        if self.interface:
            arg_type = self.interface
        else:
            # Only new_id's are returned, the only corner case here is for
            # wl_registry.bind, so no interface => Proxy
            arg_type = ":class:`pywayland.client.proxy.Proxy` of specified Interface"

        # Output the type and summary
        printer.doc(":returns:")
        with printer.indented():
            if self.summary:
                printer.docstring("{} -- {}".format(arg_type, self.summary))
            else:
                printer.docstring("{}".format(arg_type))
