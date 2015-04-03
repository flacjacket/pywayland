#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import importlib
import os
import shutil
import sys
import six.moves.urllib as urllib

from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('..'))


# We have to mock the ffi module
class Mock(MagicMock):
    @classmethod
    def __getattr__(cls, name):
        return Mock()


MOCK_MODULES = ['pywayland.ffi']
sys.modules.update((mod_name, Mock()) for mod_name in MOCK_MODULES)

# -- Build pywayland.protocol w/docs --------------------------------------

protocol_build_dir = '../pywayland/protocol/'
protocol_doc_dir = 'module/protocol'

protocol_version = '1.7.0'
protocol_source = 'http://cgit.freedesktop.org/wayland/wayland/plain/protocol/wayland.xml?id={}'.format(protocol_version)

index_header = """\
.. _protocol:

Protocol Modules
================

Wayland protocols built against Wayland {}.

.. toctree::
   :maxdepth: 2

""".format(protocol_version)

protocol_rst = """\
.. module:: pywayland.protocol.{mod_lower}

{mod_upper}
{empty:=^{len}}

.. wl_protocol:: pywayland.protocol.{mod_lower} {mod_upper}
"""


def protocol_build(output_dir):
    from pywayland.scanner import Scanner

    protocol_dest = 'wayland.xml'

    urllib.request.urlretrieve(protocol_source, protocol_dest)
    scanner = Scanner(protocol_dest)
    scanner.scan()
    scanner.output(output_dir)


# There is probably a better way to do this in Sphinx, templating or something
# ... but this works
def protocol_doc(input_dir, output_dir):
    py_files = os.listdir(input_dir)
    doc_files = [os.path.splitext(f)[0] for f in py_files
                 if f[0] != '_']

    # Write out the index file
    index_file = os.path.join(output_dir, 'index.rst')
    with open(index_file, 'w') as f:
        f.write(index_header)
        for d in doc_files:
            f.write('   {}\n'.format(d))

    for mod_lower in doc_files:
        mod = importlib.import_module('pywayland.protocol.' + mod_lower)
        for mod_upper in dir(mod):
            if mod_upper.lower() == mod_lower:
                break

        mod_len = len(mod_lower)
        doc_file = os.path.join(output_dir, '{}.rst'.format(mod_lower))
        with open(doc_file, 'w') as f:
            f.write(protocol_rst.format(
                mod_lower=mod_lower,
                mod_upper=mod_upper,
                len=mod_len,
                empty=''
            ))


# Build the protocol directoryon RTD, or if it does not exist
if os.environ.get('READTHEDOCS', None) or not os.path.exists(protocol_build_dir):
    if not os.path.exists(protocol_build_dir):
        os.makedirs(protocol_build_dir)

    protocol_build(protocol_build_dir)

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
copyright = '2015, Sean Vig'

# The short X.Y version.
version = '0.0.1'
# The full version, including alpha/beta/rc tags.
release = '0.0.1a.dev'

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
