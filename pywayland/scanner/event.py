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

from .method import Method


class Event(Method):
    """Scanner for event objects (server-side method)

    Required attributes: `name`

    Optional attributes: `since`

    Child elements: `description` and `arg``
    """
    method_type = 'event'

    def method_args(self):
        """Generator of the arguments to the method

        All arguments to be sent to `._post_event` must be passed in
        """
        for arg in self.args:
            yield arg.name

    def post_args(self):
        """Arguments sent to `._post_event`"""
        for arg in self.args:
            yield arg.name

    def output_doc_param(self, printer):
        """Aguments documented as parameters

        All arguments are event parameters.
        """
        for arg in self.args:
            arg.output_doc_param(printer)

    def output_doc_ret(self, printer):
        """Aguments documented as return values

        Nothing is returned from event calls.
        """
        return

    def output_body(self, printer):
        """Output the body of the event to the printer"""
        args = ', '.join(self.post_args())
        if args:
            printer('self._post_event({:d}, {})'.format(self.opcode, args))
        else:
            printer('self._post_event({:d})'.format(self.opcode))
