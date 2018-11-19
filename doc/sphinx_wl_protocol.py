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

import importlib
import inspect

from docutils.statemachine import ViewList
from jinja2 import Template
from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.util.docstrings import prepare_docstring
from sphinx.util.inspect import getargspec
from sphinx.util.nodes import nested_parse_with_titles


# Adapted from sphinxcontrib-httpdomain
def import_object(module_name, class_name):
    mod = importlib.import_module(module_name)
    return getattr(mod, class_name)


def format_args(func):
    arg_spec = getargspec(func)
    if arg_spec[0][0] == 'self':  # Should always be true
        del(arg_spec[0][0])
    return formatargspec(*arg_spec)


def formatargspec(*argspec):
    # most recent version of sphinx.ext.autodoc uses:
    # from sphinx.util.inspect import object_description
    # return inspect.formatargspec(*argspec, formatvalue=lambda x: '=' + object_description(x))
    # RTD uses an old sphinx version without object_description, but this doesn't seem to make any difference for this
    return inspect.formatargspec(*argspec)


wl_protocol_template = Template("""
.. autoclass:: {{ module }}.{{ class_name }}
    {% for func, opcode, sig, docs in requests %}
    .. method:: {{ func }} {{ sig }}

        .. rubric:: Request -- opcode {{ opcode}} (attached to :class:`~pywayland.server.resource.Resource` instance)

{% for doc in docs %}
        {{ doc }}{% endfor %}{% endfor %}
    {% for func, opcode, sig, docs in events %}
    .. method:: {{ func }} {{ sig }}

        .. rubric:: Event -- opcode {{ opcode}} (attached to :class:`~pywayland.client.proxy.Proxy` instance)

{% for doc in docs %}
        {{ doc }}{% endfor %}{% endfor %}
""")


class WlProtocol(Directive):
    required_arguments = 2

    def make_rst(self):
        module_name, class_name = self.arguments[:2]
        obj = import_object(module_name, class_name)
        events = [
            (event.py_func.__name__, opcode, format_args(event.py_func), prepare_docstring(event.py_func.__doc__))
            for opcode, event in enumerate(obj.events)
        ]
        reqs = [(req.py_func.__name__, opcode, format_args(req.py_func),
                 prepare_docstring(req.py_func.__doc__)) for opcode, req in enumerate(obj.requests)]
        context = {
            'module': module_name,
            'class_name': class_name,
            'obj': obj,
            'events': events,
            'requests': reqs
        }
        rst = wl_protocol_template.render(**context)
        for line in rst.splitlines():
            yield line

    def run(self):
        node = nodes.section()
        node.document = self.state.document
        result = ViewList()
        for line in self.make_rst():
            result.append(line, '<{0}>'.format(self.__class__.__name__))
        nested_parse_with_titles(self.state, result, node)
        return node.children


def setup(app):
    app.add_directive('wl_protocol', WlProtocol)
