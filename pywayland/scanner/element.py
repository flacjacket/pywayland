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

import textwrap
from typing import NamedTuple, List  # noqa: F401


Attribute = NamedTuple("Attribute", [("name", str), ("required", bool)])

Child = NamedTuple("Child", [("name", str), ("class_", object), ("required", bool), ("allow_multiple", bool)])


class Element:
    attributes = []  # type: List[Attribute]
    children = []  # type: List[Child]
    pcdata = False

    def __init__(self, element, *args, **kwargs):
        for attr in self.attributes:
            obj = element.attrib.get(attr.name)

            if not attr and attr.required:
                raise ValueError()

            name = attr.name.replace('-', '_')
            setattr(self, name, obj)

        for child in self.children:
            if child.allow_multiple:
                obj = [child.class_(elem) for elem in element.findall(child.name)]
            else:
                obj = element.find(child.name)
                if obj is not None:
                    obj = child.class_(obj)

            if not obj and child.required:
                raise ValueError(child.name)

            # We need to replace dashes with underscores
            name = child.name.replace('-', '_')
            setattr(self, name, obj)

        if self.pcdata:
            text = element.text
            # We need to strip each line while keeping paragraph breaks
            if text:
                self.text = textwrap.dedent(text.expandtabs(8).rstrip().lstrip('\n'))
            else:
                self.text = None
