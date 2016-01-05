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

from __future__ import absolute_import

import os
import shlex
import subprocess
import sys

from setuptools import setup
from distutils.cmd import Command
from distutils.command.build import build
from setuptools.command.install import install

sys.path.insert(0, 'pywayland')

# Default locations
xml_file = '/usr/share/wayland/wayland.xml'


def run_scanner(input_xml, output_path):
    """Run the pywayland scanner on the given XML file"""
    # We'll directly import the scanner, so we can build the protocol before
    # the cffi module has been compiled
    from scanner.scanner import Scanner

    # Ensure the protocol dir exists
    if not os.path.isdir(output_path):
        os.makedirs(output_path, 0o775)

    # Run and scan the xml file
    scanner = Scanner(input_xml)
    scanner.output(output_path)


def generate_protocol(wayland_xml, output_path):
    """Generate all Wayland XML protocol files"""
    # We're given the wayland.xml file, lets run that
    run_scanner(wayland_xml, output_path)


def generate_external_protocol(output_path):
    modules = []

    # try to generate the wayland-protocol interfaces
    try:
        protocols_dir = pkgconfig('wayland-protocols', 'pkgdatadir')
    except subprocess.CalledProcessError:
        raise OSError("Unable to find wayland protocls using pkgconfig")
    else:
        # walk through all files in the directory
        for dirpath, _, filenames in os.walk(protocols_dir):
            for filename in filenames:
                full_filename = os.path.join(dirpath, filename)
                base, ext = os.path.splitext(filename)
                # if the file is an xml, generate the protocol
                if ext == '.xml':
                    run_scanner(full_filename, output_path)
                    module = base.replace('-', '_')
                    modules.append(module)
    return modules


def pkgconfig(package, variable):
    cmd = 'pkg-config --variable={} {}'.format(variable, package)
    output = subprocess.check_output(shlex.split(cmd)).decode().strip()
    return output


class GenerateProtocolCommand(Command):
    """Generate the pywayland protocol files"""

    description = "Generate the pywayland protocol files"
    user_options = [
        ('xml-file=', None, 'Location of wayland.xml protocol file'),
        ('output-dir=', None, 'Output location for protocol python files'),
        ('wayland-protocols', None, 'Force generation of external protocols from wayland-protocols'),
        ('no-wayland-protocols', None, 'Disable generation of external protocols from wayland-protocols')
    ]
    boolean_options = ['wayland-protocols', 'no-wayland-protocols']

    def initialize_options(self):
        self.xml_file = xml_file
        self.output_dir = './pywayland/protocol'
        self.wayland_protocols = False
        self.no_wayland_protocols = False

    def finalize_options(self):
        assert os.path.exists(self.xml_file), (
            "Wayland protocol file {} does not exist".format(self.xml_file)
        )

    def run(self):
        # Generate the wayland interface
        generate_protocol(self.xml_file, self.output_dir)

        # Unless users says don't build protocols, try to build them
        if not self.no_wayland_protocols:
            try:
                generate_external_protocol(self.output_dir)
            except:
                # but only complain if we ask specifically to build them
                if self.wayland_protocols:
                    raise


class BuildCommand(build):
    user_options = build.user_options + [
        ('xml-file=', None, 'Location of wayland.xml protocol file'),
        ('wayland-protocols', None, 'Force generation of external protocols from wayland-protocols'),
        ('no-wayland-protocols', None, 'Disable generation of external protocols from wayland-protocols')
    ]
    boolean_options = build.boolean_options + ['wayland-protocols', 'no-wayland-protocols']

    def initialize_options(self):
        self.xml_file = xml_file
        self.wayland_protocols = False
        self.no_wayland_protocols = False
        build.initialize_options(self)

    def finalize_options(self):
        assert os.path.exists(self.xml_file), (
            "Wayland protocol file does not exist at default location, {}, "
            "please specify protocol file".format(xml_file)
        )
        build.finalize_options(self)

    def run(self):
        # Generate the wayland interface
        protocol_dir = './pywayland/protcool'
        generate_protocol(self.xml_file, protocol_dir)
        self.distribution.packages.append('pywayland.protocol.wayland')

        # Run the external protocol generation
        if not self.no_wayland_protocols:
            # as above, we'll try generating them unless explicitly told not
            # to, but only raise the error if specifically told to
            try:
                modules = generate_external_protocol(protocol_dir)
            except:
                if self.wayland_protocols:
                    raise
            else:
                # Add the protocol modules to be copied
                for module in modules:
                    self.distribution.packages.append('pywayland.protocol.{}'.format(module))

        build.run(self)


class InstallCommand(install):
    user_options = install.user_options + [
        ('xml-file=', None, 'Location of wayland.xml protocol file'),
        ('wayland-protocols', None, 'Force generation of external protocols from wayland-protocols'),
        ('no-wayland-protocols', None, 'Disable generation of external protocols from wayland-protocols')
    ]
    boolean_options = install.boolean_options + ['wayland-protocols', 'no-wayland-protocols']

    def initialize_options(self):
        self.xml_file = '/usr/share/wayland/wayland.xml'
        self.wayland_protocols = False
        self.no_wayland_protocols = False

        install.initialize_options(self)

    def finalize_options(self):
        assert os.path.exists(self.xml_file), (
            "Wayland protocol file does not exist at default location, {}, "
            "please specify protocol file".format(xml_file)
        )
        install.finalize_options(self)

    def run(self):
        protocol_dir = './pywayland/protocol'

        # Run the wayland protocol generation
        generate_protocol(xml_file, protocol_dir)

        # Run the external protocol generation
        if not self.no_wayland_protocols:
            # as above, we'll try generating them unless explicitly told not
            # to, but only raise the error if specifically told to
            try:
                modules = generate_external_protocol(protocol_dir)
            except:
                if self.wayland_protocols:
                    raise
            else:
                # Add the protocol modules to be copied
                for module in modules:
                    self.distribution.packages.append('pywayland.protocol.{}'.format(module))

        install.run(self)


description = 'Python bindings for the libwayland library written in pure Python'

# Just pull the long description from the README
try:
    rst_input = open('README.rst').read().split('\n')
except:
    long_description = ""
else:
    # For the purposes of uploading, we'll pull the version of Wayland here
    try:
        from pywayland import __wayland_version__
    except ImportError:
        long_description = '\n' + '\n'.join(rst_input)
    else:
        rst_head = rst_input[:3]
        rst_body = rst_input[3:]
        version = 'Built against Wayland {}'.format(__wayland_version__)

        long_description = '\n' + '\n'.join(
            rst_head + [version, ''] + rst_body
        )

# Check if we're running PyPy, cffi can't be updated
if '_cffi_backend' in sys.builtin_module_names:
    import _cffi_backend
    requires_cffi = 'cffi==' + _cffi_backend.__version__
else:
    requires_cffi = 'cffi>=1.1.0'

# PyPy < 2.6 hack, can be dropped when PyPy3 2.6 is released
if requires_cffi.startswith('cffi==0.'):
    cffi_args = dict(
        ext_package='pywayland'
    )
else:
    cffi_args = dict(
        cffi_modules=['pywayland/ffi_build.py:ffi']
    )

dependencies = ['six>=1.4.1', requires_cffi]

if sys.version_info < (3, 4):
    dependencies.append('enum34')

classifiers = [
    'Development Status :: 2 - Pre-Alpha',
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: POSIX',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: Implementation :: CPython',
    'Programming Language :: Python :: Implementation :: CPython',
    'Programming Language :: Python :: Implementation :: PyPy',
    'Topic :: Desktop Environment :: Window Managers',
    'Topic :: Software Development :: Libraries'
]

modules = [
    'pywayland',
    'pywayland.client',
    'pywayland.protocol',
    'pywayland.scanner',
    'pywayland.server'
]

setup(
    name='pywayland',
    version='0.0.1a.dev5',
    author='Sean Vig',
    author_email='sean.v.775@gmail.com',
    url='http://github.com/flacjacket/pywayland',
    description=description,
    long_description=long_description,
    license='Apache License 2.0',
    classifiers=classifiers,
    install_requires=dependencies,
    setup_requires=dependencies,
    packages=modules,
    entry_points={
        'console_scripts': [
            'pywayland-scanner = pywayland.pywayland_scanner:main'
        ]
    },
    zip_safe=False,
    cmdclass={
        'build': BuildCommand,
        'install': InstallCommand,
        'generate_protocol': GenerateProtocolCommand
    },
    **cffi_args
)
