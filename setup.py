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
import subprocess
import sys

from setuptools import setup
from distutils.command.build import build
from setuptools.command.install import install
from setuptools.command.sdist import sdist

# we need this to import the scanner module directly so we can build the
# protocol before the cffi module has been compiled
sys.path.insert(0, 'pywayland')

from version import __version__ as pywayland_version

default_xml_file = '/usr/share/wayland/wayland.xml'


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
            from scanner.__main__ import pkgconfig
            # try to figure out where the main wayland protocols are installed
            try:
                data_dir = pkgconfig('wayland-scanner', 'pkgdatadir')
            except subprocess.CalledProcessError:
                # silently fallback to the default
                self.xml_file = default_xml_file
            else:
                self.xml_file = os.path.join(data_dir, 'wayland.xml')

            self.output_dir = './pywayland/protocol'
            self.wayland_protocols = False
            self.no_wayland_protocols = False

            klass.initialize_options(self)

        def finalize_options(self):
            assert os.path.exists(self.xml_file), (
                "Specified Wayland protocol file, {}, does not exist "
                "please specify valid protocol file".format(self.xml_file)
            )

            klass.finalize_options(self)

        def run(self):
            from scanner.scanner import Scanner
            from scanner.__main__ import get_wayland_protocols

            # Generate the wayland interface by default
            input_files = [self.xml_file]
            modules = ["wayland"]

            # Unless users says don't build protocols, try to build them
            if not self.no_wayland_protocols:
                try:
                    protocol_modules, protocol_files = get_wayland_protocols()
                    input_files += protocol_files
                    modules += protocol_modules
                except:
                    # but only complain if we ask specifically to build them
                    if self.wayland_protocols:
                        raise

            # Ensure the output dir exists
            if not os.path.isdir(self.output_dir):
                os.makedirs(self.output_dir, 0o775)

            # Run and scan all the above found xml files
            for input_xml in input_files:
                scanner = Scanner(input_xml)
                scanner.output(self.output_dir)

            # if we're building or installing, add the modules we generated
            if hasattr(self, 'distribution'):
                for module in modules:
                    self.distribution.packages.append('pywayland.protocol.{}'.format(module))

            klass.run(self)

    if hasattr(klass, "user_options"):
        ProtocolCommand.user_options += klass.user_options
    if hasattr(klass, "boolean_options"):
        ProtocolCommand.boolean_options += klass.boolean_options

    return ProtocolCommand


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
    version=pywayland_version,
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
        'sdist': SdistCommand
    },
    cffi_modules=['pywayland/ffi_build.py:ffi']
)
