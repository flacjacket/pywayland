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
import xml.etree.ElementTree as ET

from .element import Element
from .printer import Printer

copyright_default = """\
# Copyright 2015 Sean Vig
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License."""


@dataclass(frozen=True)
class Copyright(Element):
    text: str

    @classmethod
    def parse(cls, element: ET.Element) -> "Copyright":
        text = cls.parse_pcdata(element)
        assert text is not None

        return cls(text=text)

    def output(self, printer: Printer) -> None:
        for line in self.text.split("\n"):
            if line:
                printer("# " + line.rstrip())
            else:
                printer("#")
