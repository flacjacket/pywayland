#!/usr/bin/env python3

import importlib
import os
import shutil
import sys
import re

# -- Mock necessary classes -----------------------------------------------
from unittest.mock import MagicMock

import sphinx_rtd_theme

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath(".."))

MOCK_MODULES = ["pywayland._ffi"]
sys.modules.update((mod_name, MagicMock()) for mod_name in MOCK_MODULES)

# -- Build pywayland.protocol w/docs --------------------------------------
from protocol_build import protocols_build, protocols_version, wayland_version

from pywayland import __version__

protocol_build_dir = "../pywayland/protocol/"
protocol_doc_dir = "module/protocol"

index_header = f"""\
.. _protocol:

Protocol Modules
================

Wayland protocols built against Wayland {wayland_version} and Wayland Protocols {protocols_version}.

.. toctree::
   :maxdepth: 2

"""

protocol_header = """\
.. module:: pywayland.protocol.{module}

{module} Module
{empty:=^{len}}======="""

protocol_rst = """\
{protocol}
{empty:-^{len}}

.. wl_protocol:: pywayland.protocol.{module} {protocol}"""


# There is probably a better way to do this in Sphinx, templating or something
# ... but this works
def protocol_doc(input_dir, output_dir):
    modules = os.listdir(input_dir)
    modules = [
        module.rstrip(".py")
        for module in modules
        if os.path.isfile(os.path.join(input_dir, module)) and module != "__init__.py"
    ]

    existing_files = [
        filename for filename in os.listdir(output_dir) if filename != "index.rst"
    ]
    rm_files = [
        filename
        for filename in existing_files
        if os.path.splitext(filename)[0] not in modules
    ]
    for rm_file in rm_files:
        if os.path.isdir(rm_file):
            shutil.rmtree(os.path.join(output_dir, rm_file))
        else:
            os.remove(os.path.join(output_dir, rm_file))

    # Write out the index file
    index_file = os.path.join(output_dir, "index.rst")
    if os.path.exists(index_file):
        with open(index_file) as f:
            existing_index = f.read()
    else:
        existing_index = ""

    generated_index = index_header + "".join(f"   {m}\n" for m in sorted(modules))

    if existing_index != generated_index:
        with open(index_file, "w") as f:
            f.write(generated_index)

    for module in modules:
        output = [protocol_header.format(module=module, len=len(module), empty="")]

        # get all the interfaces that we want to document
        protocol_file = os.path.join(input_dir, f"{module}.py")
        interfaces = []
        with open(protocol_file) as f:
            for line in f:
                match = re.search(r"class (\w+)\(Interface\):", line)
                if match:
                    interfaces.append(match.group(1))

        # build the rst for each interface
        for interface in interfaces:
            mod = importlib.import_module(f"pywayland.protocol.{module}")

            if interface not in dir(mod):
                raise RuntimeError(f"Unable to find module: {interface}, {mod}")

            output.append(
                protocol_rst.format(
                    module=module, protocol=interface, len=len(interface), empty=""
                )
            )

        # build the index.rst for the module
        module_file = os.path.join(output_dir, f"{module}.rst")
        protocol_output = "\n\n".join(output)

        # if file exists and is unchanged, skip
        if os.path.exists(module_file):
            with open(module_file) as f:
                existing_output = f.read()

            if existing_output == protocol_output:
                continue

        with open(module_file, "w") as f:
            f.write("\n\n".join(output))


# Build the protocol directory on RTD
if os.environ.get("READTHEDOCS", None):
    protocols_build(protocol_build_dir)

# Re-build the protocol documentation directory
if not os.path.exists(protocol_doc_dir):
    os.makedirs(protocol_doc_dir)

protocol_doc(protocol_build_dir, protocol_doc_dir)

# -- General configuration ------------------------------------------------
extensions = ["sphinx.ext.autodoc", "sphinx_wl_protocol"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "pywayland"
copyright = "2016, Sean Vig"

# The short X.Y version.
version = __version__.split("a")[0]
# The full version, including alpha/beta/rc tags.
release = __version__

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["_build"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"


# -- Options for HTML output ----------------------------------------------

# Set the html_theme when building locally
html_theme = "sphinx_rtd_theme"

# Output file base name for HTML help builder.
htmlhelp_basename = "pywaylanddoc"


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    ("index", "pywayland.tex", "pywayland Documentation", "Sean Vig", "manual"),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [("index", "pywayland", "pywayland Documentation", ["Sean Vig"], 1)]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        "index",
        "pywayland",
        "pywayland Documentation",
        "Sean Vig",
        "pywayland",
        "Python bindings for the libwayland library",
        "Miscellaneous",
    ),
]
