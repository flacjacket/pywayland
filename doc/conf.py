#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import importlib
import os
import shutil
import sys

# -- Monkey patch to remove external image warning ------------------------

import sphinx.environment
from docutils.utils import get_source_line


def _warn_node(self, msg, node):
    if not msg.startswith('nonlocal image URI found:'):
        self._warnfunc(msg, '%s:%s' % get_source_line(node))

sphinx.environment.BuildEnvironment.warn_node = _warn_node


# -- Mock necessary classes -----------------------------------------------

from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('..'))


MOCK_MODULES = ['pywayland._ffi']
sys.modules.update((mod_name, MagicMock()) for mod_name in MOCK_MODULES)

from pywayland import __version__

# -- Build pywayland.protocol w/docs --------------------------------------

from protocol_build import wayland_version, wayland_build, protocols_version, protocols_build

protocol_build_dir = '../pywayland/protocol/'
protocol_doc_dir = 'module/protocol'

index_header = """\
.. _protocol:

Protocol Modules
================

Wayland protocols built against Wayland {} and Wayland Protocols {}.

.. toctree::
   :maxdepth: 2

""".format(wayland_version, protocols_version)

protocol_header = """\
.. module:: pywayland.protocol.{module}

{module} Module
{empty:=^{len}}=======

.. toctree::
   :maxdepth: 2

"""

protocol_rst = """\
.. module:: pywayland.protocol.{module}.{protocol}

{protocol_upper}
{empty:=^{len}}

.. wl_protocol:: pywayland.protocol.{module}.{protocol} {protocol_upper}
"""


# There is probably a better way to do this in Sphinx, templating or something
# ... but this works
def protocol_doc(input_dir, output_dir):
    _, modules, _ = next(os.walk(input_dir))
    modules = [x for x in modules if not x.startswith('__')]

    # Write out the index file
    index_file = os.path.join(output_dir, 'index.rst')
    with open(index_file, 'w') as f:
        f.write(index_header)
        for m in sorted(modules):
            f.write('   {}/index\n'.format(m))

    for module in modules:
        module_dir = os.path.join(output_dir, module)
        os.makedirs(module_dir)

        # get all the python files that we want to document
        _, _, doc_files = next(os.walk(os.path.join(input_dir, module)))
        doc_files = [os.path.splitext(doc_file)[0] for doc_file in doc_files
                     if doc_file != '__init__.py' and os.path.splitext(doc_file)[1] == '.py']

        # build the index.rst for the module
        index_file = os.path.join(module_dir, 'index.rst')
        with open(index_file, 'w') as f:
            f.write(protocol_header.format(
                module=module,
                len=len(module),
                empty=''
            ))
            for d in sorted(doc_files):
                f.write('   {}\n'.format(d))

        # build the .rst files for each protocol
        for doc_file in doc_files:
            mod = importlib.import_module('pywayland.protocol.{}.{}'.format(module, doc_file))
            # Get out the name of the class in the module
            for mod_upper in dir(mod):
                if mod_upper.lower() == doc_file:
                    break

            protocol_len = len(doc_file)
            doc = os.path.join(module_dir, '{}.rst'.format(doc_file))
            with open(doc, 'w') as f:
                f.write(protocol_rst.format(
                    module=module,
                    protocol=doc_file,
                    protocol_upper=mod_upper,
                    len=protocol_len,
                    empty=''
                ))


# Build the protocol directory on RTD
if os.environ.get('READTHEDOCS', None):
    wayland_build(protocol_build_dir)
    protocols_build(protocol_build_dir)

# Re-build the protocol documentation directory
if os.path.exists(protocol_doc_dir):
    shutil.rmtree(protocol_doc_dir)
os.makedirs(protocol_doc_dir)

protocol_doc(protocol_build_dir, protocol_doc_dir)

# -- General configuration ------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx_wl_protocol'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'pywayland'
copyright = '2016, Sean Vig'

# The short X.Y version.
version = __version__.split("a")[0]
# The full version, including alpha/beta/rc tags.
release = __version__

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'


# -- Options for HTML output ----------------------------------------------

# Set the html_theme when building locally
if not os.environ.get('READTHEDOCS', None):
    import sphinx_rtd_theme
    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# Output file base name for HTML help builder.
htmlhelp_basename = 'pywaylanddoc'


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    ('index', 'pywayland.tex', 'pywayland Documentation',
     'Sean Vig', 'manual'),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'pywayland', 'pywayland Documentation',
     ['Sean Vig'], 1)
]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    ('index', 'pywayland', 'pywayland Documentation',
     'Sean Vig', 'pywayland', 'Python bindings for the libwayland library',
     'Miscellaneous'),
]
