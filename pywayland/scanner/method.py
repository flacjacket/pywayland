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

import abc
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

from .argument import Argument
from .description import Description
from .element import Element
from .printer import Printer


@dataclass(frozen=True)  # type: ignore[misc]
class Method(Element, abc.ABC):
    """Scanner for methods

    Corresponds to event and requests defined on an interface
    """

    name: str
    since: Optional[str]
    description: Optional[Description]
    arg: List[Argument]

    def imports(
        self, interface: str, module_imports: Dict[str, str]
    ) -> List[Tuple[str, str]]:
        """Get the imports required for each of the interfaces

        :param interface:
            The name of the interface that the method is a part of.
        :param module_imports:
            A mapping from the name of an interface in the associated
            module that the interface comes from.
        :return:
            A list of 2-tuples, each specifying the path to an imported
            module and the imported class.
        """
        current_protocol = module_imports[interface]

        imports = []
        for arg in self.arg:
            if arg.interface is None:
                continue

            if arg.interface == interface:
                continue

            import_class = arg.interface_class
            import_protocol = module_imports[arg.interface]

            if current_protocol == import_protocol:
                import_path = ".{}".format(arg.interface)
            else:
                import_path = "..{}".format(import_protocol)

            imports.append((import_path, import_class))

        return imports

    @property
    @abc.abstractmethod
    def method_type(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def method_args(self) -> Iterable[str]:
        pass

    @abc.abstractmethod
    def output_doc_params(self, printer: Printer) -> None:
        pass

    @abc.abstractmethod
    def output_body(self, printer: Printer, opcode: int) -> None:
        pass

    def output(
        self,
        printer: Printer,
        opcode: int,
        in_class: str,
        module_imports: Dict[str, str],
    ) -> None:
        """Generate the output for the given method to the printer"""
        if len(self.arg) > 0:
            printer(f"@{in_class}.{self.method_type}(")
            with printer.indented():
                for arg in self.arg:
                    arg.output(printer)
                if self.since:
                    printer(f"version={self.since},")
            printer(")")
        else:
            if self.since:
                printer(f"@{in_class}.{self.method_type}(version={self.since})")
            else:
                printer(f"@{in_class}.{self.method_type}()")

        # Generate the definition of the method and args
        args = ", ".join(["self"] + list(self.method_args))
        printer("def {}({}):".format(self.name, args))

        with printer.indented():
            # Write the documentation
            self.output_doc(printer)
            # Write out the body of the method
            self.output_body(printer, opcode)

    def output_doc(self, printer: Printer) -> None:
        """Output the documentation for the interface"""
        if self.description:
            self.description.output(printer)
        else:
            printer('"""' + self.name)
        # Parameter and returns documentation
        if self.arg:
            printer()
            self.output_doc_params(printer)
        printer('"""')
