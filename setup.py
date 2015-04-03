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
import platform
import sys

from setuptools import setup
from distutils.command.build import build

protocol_dir = './pywayland/protocol'


def build_protocol(input_file):
    """Build the ./pywayland/protocol/ directory from the given xml file"""
    from pywayland.scanner.scanner import Scanner

    # Ensure the protocol dir exists
    if not os.path.isdir(protocol_dir):
        os.makedirs(protocol_dir, 0o775)

    # Run and scan the xml file
    scanner = Scanner(input_file)
    scanner.scan()
    scanner.output(protocol_dir)


# Adapted from http://github.com/xattr/xattr
class module_build(build):
    """
    This is a shameful hack to ensure that cffi is present when we specify
    ext_modules. We can't do this eagerly because setup_require hasn't run yet.

    Furthermore, we also need to build the pywayland.protocol module and add it
    to the packages.  This must also be held off until setup_require has run.
    """
    user_options = build.user_options + [
        ('xml-file=', None, 'Location of wayland.xml protocol file')
    ]

    def initialize_options(self):
        build.initialize_options(self)
        self.xml_file = '/usr/share/wayland/wayland.xml'

    def finalize_options(self):
        from pywayland import ffi
        self.distribution.ext_modules = [ffi.verifier.get_extension()]

        build_protocol(self.xml_file)
        self.distribution.packages.append('pywayland.protocol')

        build.finalize_options(self)


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
    'Programming Language :: Python :: Implementation :: CPython',
    'Programming Language :: Python :: Implementation :: PyPy',
    'Topic :: Desktop Environment :: Window Managers',
    'Topic :: Software Development :: Libraries'
]

dependencies = ['six>=1.4.1']

modules = [
    'pywayland.client',
    'pywayland.scanner'
]

if sys.version_info < (3, 4):
    dependencies.append('enum34')

if platform.python_implementation() != "PyPy":
    dependencies.append('cffi>=0.9')

setup(
    name='pywayland',
    version='0.0.1a.dev3',
    author='Sean Vig',
    author_email='sean.v.775@gmail.com',
    url='http://github.com/flacjacket/pywayland',
    description=description,
    long_description=long_description,
    license='Apache License 2.0',
    classifiers=classifiers,
    install_requires=dependencies,
    setup_requires=dependencies,
    packages=['pywayland'] + modules,
    entry_points={
        'console_scripts': [
            'pywayland-scanner = pywayland.pywayland_scanner:main'
        ]
    },
    zip_safe=False,
    ext_package='_pywayland',
    cmdclass={
        'build': module_build
    }
)
