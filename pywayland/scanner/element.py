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

from typing import List, Optional, TypeVar, Type
import abc
import textwrap
import xml.etree.ElementTree as ET

T = TypeVar("T", bound="Element")


class Element(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def parse(cls: Type[T], element: ET.Element) -> T:
        pass

    @staticmethod
    def parse_attribute(element: ET.Element, name: str) -> str:
        obj = Element.parse_optional_attribute(element, name)
        if obj is None:
            raise ValueError()

        return obj

    @staticmethod
    def parse_optional_attribute(element: ET.Element, name) -> Optional[str]:
        obj = element.attrib.get(name)
        return obj

    @staticmethod
    def parse_child(element: ET.Element, child_class: Type[T], name: str) -> T:
        obj = Element.parse_optional_child(element, child_class, name)
        if obj is None:
            raise ValueError()

        return obj

    @staticmethod
    def parse_optional_child(
        element: ET.Element, child_class: Type[T], name: str
    ) -> Optional[T]:
        obj = element.find(name)
        if obj is None:
            return None

        return child_class.parse(obj)

    @staticmethod
    def parse_repeated_child(
        element: ET.Element, child_class: Type[T], name: str
    ) -> List[T]:
        obj = [child_class.parse(elem) for elem in element.findall(name)]
        return obj

    @staticmethod
    def parse_pcdata(element: ET.Element) -> Optional[str]:
        text = element.text
        if text:
            # We need to strip each line while keeping paragraph breaks
            return textwrap.dedent(text.expandtabs(8).rstrip().lstrip("\n"))

        return None
