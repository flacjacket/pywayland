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
from setuptools.command.sdist import sdist

sys.path.insert(0, 'pywayland')

default_xml_file = '/usr/share/wayland/wayland.xml'


def pkgconfig(package, variable):
    cmd = 'pkg-config --variable={} {}'.format(variable, package)
    output = subprocess.check_output(shlex.split(cmd)).decode().strip()
    return output


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
                file_path = os.path.join(dirpath, filename)
                file_base, file_ext = os.path.splitext(filename)
                # if the file is an xml, generate the protocol
                if file_ext == '.xml':
                    run_scanner(file_path, output_path)
                    modules.append(file_base.replace('-', '_'))
    return modules


def get_protocol_command(klass):
    class ProtocolCommand(klass):
        description = "Generate the pywayland protocol files"
        user_options = [
            ('xml-file=', None, 'Location of wayland.xml protocol file'),
            ('output-dir=', None, 'Output location for protocol python files'),
            ('wayland-protocols', None, 'Force generation of external protocols from wayland-protocols'),
            ('no-wayland-protocols', None, 'Disable generation of external protocols from wayland-protocols')
        ]
        boolean_options = ['wayland-protocols', 'no-wayland-protocols']

        def initialize_options(self):
            try:
                data_dir = pkgconfig('wayland-scanner', 'pkgdatadir')
            except subprocess.CalledProcessError:
                self.xml_file = default_xml_file
            else:
                self.xml_file = os.path.join(data_dir, 'wayland.xml')
            self.output_dir = './pywayland/protocol'
            self.wayland_protocols = False
            self.no_wayland_protocols = False

            if klass is not Command:
                klass.initialize_options(self)

        def finalize_options(self):
            assert os.path.exists(self.xml_file), (
                "Specified Wayland protocol file, {}, does not exist "
                "please specify valid protocol file".format(self.xml_file)
            )

            if klass is not Command:
                klass.finalize_options(self)

        def run(self):
            # Generate the wayland interface
            run_scanner(self.xml_file, self.output_dir)
            # Unless users says don't build protocols, try to build them
            if not self.no_wayland_protocols:
                try:
                    modules = generate_external_protocol(self.output_dir)
                except:
                    # but only complain if we ask specifically to build them
                    if self.wayland_protocols:
                        raise
                    modules = []
            # if we're building or installing, add the modules we generated
            if hasattr(self, 'distribution'):
                self.distribution.packages.append('pywayland.protocol.wayland')
                for module in modules:
                    self.distribution.packages.append('pywayland.protocol.{}'.format(module))

            if klass is not Command:
                klass.run(self)

    if hasattr(klass, "user_options"):
        ProtocolCommand.user_options += klass.user_options
    if hasattr(klass, "boolean_options"):
        ProtocolCommand.boolean_options += klass.boolean_options

    return ProtocolCommand


GenerateProtocolCommand = get_protocol_command(Command)
BuildCommand = get_protocol_command(build)
InstallCommand = get_protocol_command(install)
SdistCommand = get_protocol_command(sdist)

description = 'Python bindings for the libwayland library written in pure Python'

# For the purposes of uploading to PyPI, we'll get the version of Wayland here
try:
    from pywayland import __wayland_version__
    rst_input = open('README.rst').read().split('\n')
except:
    long_description = ""
else:
    version = 'Built against Wayland {}\n'.format(__wayland_version__)
    rst_input.insert(3, version)

    long_description = '\n' + '\n'.join(rst_input)

# Check if we're running PyPy, cffi can't be updated
if '_cffi_backend' in sys.builtin_module_names:
    import _cffi_backend
    if _cffi_backend.__version__ < "1.4.2":
        raise ValueError("PyPy version is too old, must support cffi>=1.4.2 (PyPy >= 5.0.0)")
    requires_cffi = 'cffi==' + _cffi_backend.__version__
else:
    requires_cffi = "cffi>=1.4.2"

dependencies = ["six>=1.4.1", requires_cffi]

if sys.version_info < (3, 4):
    dependencies.append("enum34")

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
    version='0.0.1a.dev6',
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
        'generate_protocol': GenerateProtocolCommand,
        'build': BuildCommand,
        'install': InstallCommand,
        'sdist': SdistCommand
    },
    cffi_modules=['pywayland/ffi_build.py:ffi']
)
