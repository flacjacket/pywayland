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

from .enum import Enum
from .event import Event
from .request import Request

import itertools


class Interface(object):
    def __init__(self, iface):
        """Scanner for interface objects

        Required attributes: `name` and `version`

        Child elements: `description`, `request`, `event`, `enum`
        """
        self._iface = iface
        attrib = iface.attrib
        self.name = attrib['name']
        self.version = int(attrib['version'])

    @property
    def file_name(self):
        """Returns the file name of the interface

        Trim the 'wl_' from the specified interface name.
        """
        return ''.join(self.name.split('_')[1:]) + '.py'

    @property
    def class_name(self):
        """Returns the name of the class of the interface

        Trim the 'wl_' from the specified interface, and capitalize the first
        letter of each word, dropping the underscores.
        """
        return ''.join(x.capitalize() for x in self.name.split('_')[1:])

    def scan(self):
        """Scan the interface"""
        description = self._iface.find('description')
        self.summary = description.attrib['summary']
        self.description = description.text.strip()

        self.enums = [Enum(enum) for enum in self._iface.findall('enum')]
        self.events = [Event(event, i) for i, event in enumerate(self._iface.findall('event'))]
        self.requests = [Request(request, i) for i, request in enumerate(self._iface.findall('request'))]

        for item in itertools.chain(self.enums, self.events, self.requests):
            item.scan()

    def output(self, printer):
        """Generate the output for the interface to the printer"""
        printer.initialize_file()
        printer()

        imports = set(_import for method in itertools.chain(self.requests, self.events)
                      for _import in method.get_imports(self.name))
        printer('from pywayland.interface import Interface, InterfaceMeta')
        for _import in sorted(imports):
            printer('from .{} import {}'.format(_import.lower(), _import))
        printer()
        if self.enums:
            printer('import enum')
        printer('import six')
        printer()
        printer()

        printer('@six.add_metaclass(InterfaceMeta)')
        printer('class {}(Interface):'.format(self.class_name))
        printer.inc_level()
        printer('"""{}'.format(self.summary))
        printer()
        for line in self.description.split('\n'):
            printer(line.strip())
        printer('"""')
        printer('name = "{}"'.format(self.name))
        printer('version = {:d}'.format(self.version))
        for enum in self.enums:
            printer()
            enum.output(printer)
        printer.dec_level()

        for method in itertools.chain(self.requests, self.events):
            printer()
            printer()
            method.output(printer, self.class_name)

        printer()
        printer()
        printer('{}._gen_c()'.format(self.class_name))
