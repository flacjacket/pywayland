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

import platform

from setuptools import setup
from distutils.command.build import build


# Adapted from http://github.com/xattr/xattr
class module_build(build):
    """
    This is a shameful hack to ensure that cffi is present when we specify
    ext_modules. We can't do this eagerly because setup_require hasn't run yet.
    """
    def finalize_options(self):
        from pywayland import ffi
        self.distribution.ext_modules = [ffi.verifier.get_extension()]
        build.finalize_options(self)


description = 'Python bindings for the libwayland library written in pure Python'

long_description = """\
PyWayland provides a wrapper to libwayland using the CFFI library to provide
access to the Wayland library calls.

Built against Wayland 1.7.0.
"""

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

if platform.python_implementation() != "PyPy":
    dependencies.append('cffi>=0.9')

setup(
    name='pywayland',
    version='0.0.1a.dev',
    author='Sean Vig',
    author_email='sean.v.775@gmail.com',
    url='http://github.com/flacjacket/pywayland',
    description=description,
    license='Apache License 2.0',
    classifiers=classifiers,
    install_requires=dependencies,
    setup_requires=dependencies,
    packages=['pywayland'],
    zip_safe=False,
    ext_package='_pywayland',
    cmdclass={
        'build': module_build
    }
)
