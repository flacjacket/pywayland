.. _install:

Installation
============

To install PyWayland, you will need to have a base set of dependencies
installed.  This should be all the configuration that is required to run the
packaged version on PyPI_.  The additional steps to build and install from
source are outlined below.

If you have any problems with anything outlined here, `feedback is greatly
appreciated <https://github.com/flacjacket/pywayland/issues>`_.

.. _PyPI: https://pypi.python.org/pypi/pywayland

External Dependencies
---------------------

In order to run PyWayland, you will need to have installed the Wayland
libraries and headers such that they can be found by CFFI.  This can be done
with the ``libwayland-dev`` apt package; however, note that it is probably best
to use the most recent version of Wayland available from the `Wayland
releases`_ site, and the pip package will try to track the most recent version.

You will also need to have the Python headers installed and a version of GCC to
compile the cffi library.  The headers are typically available through the
``python-dev`` package.

Optionally, you can have installed the ``wayland-protocols`` package, also
available from the `Wayland releases`_ page.  The package uploaded to PyPI will
already have these protocols included, so this is only needed if you plan on
installing from source.

Installing with pip
-------------------

Once the external dependencies are in place you should just be able to run::

    $ pip install pywayland

Any additional unfulfilled dependencies should be downloaded.

.. _install-source:

Installing from Source
----------------------

You can download and run PyWayland from source, which will not only give you
the latest improvements and fixes, but will let you build the protocol files
against a different version than is available through pip (the version of
Wayland the protocol is compiled against is listed on the top of the PyPI_
page).

Getting the Source
^^^^^^^^^^^^^^^^^^

You can download the most recent version of PyWayland from the `git
repository`_, or clone the repository as::

    $ git clone https://github.com/flacjacket/pywayland.git

.. _git repository: https://github.com/flacjacket/pywayland

Python Dependencies
^^^^^^^^^^^^^^^^^^^

PyWayland depends on a minimal set of dependencies.  All Python version require
cffi_ (to perform Wayland library calls), which can be pip installed for
non-PyPy installations.  Note that PyPy platforms ship with cffi.

.. _cffi: https://cffi.readthedocs.org/en/latest/

Generating the Wayland Protocol
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

At this point, you have the base PyWayland module, which contains some core
objects and objects specific to client and server implementations.  The client
and server exchange messages defined in the Wayland protocol, which is an XML
file that ships with Wayland.  The scanner parses this XML file and generates
the relevant objects.

If the Wayland protocol file is in the default location
(``/usr/share/wayland/wayland.xml``) or can be found with ``pkg-config``, you
should be able to build the protocol files without any problems::

    $ python -m pywayland.scanner

This will output the protocol files to the directory ``./pywayland/protocol/``.
The input file and the output directory can be set from the command line
options, see ``python -m pywayland.scanner -h`` for more information.

Running PyWayland inplace
^^^^^^^^^^^^^^^^^^^^^^^^^

Once the protocol files are created, you can generate the cffi module.  Note:
this is only required if you want to run from the source in place.  If the
libwayland header files are correctly installed, you will just need to run::

    $ python pywaland/ffi_build.py

At this point, you should be able to use the PyWayland library.  You can check
that you have everything installed correctly by running the associated
test-suite (note that you will also need ``pytest`` to run the tests).  Simply
run::

    $ pytest

from the root directory.

Installing PyWayland
^^^^^^^^^^^^^^^^^^^^

The package can be installed from source using typical ``setup.py``
mechanisms::

    $ python setup.py install

Additional arguments can be used to automatically generate the Wayland
protocols for the standard Wayland package (which will fail if it cannot run)
and the wayland-protocols package (which will be attempted by default, but will
not raise an error if it fails).

If you have any problems or have any feedback, please report back to the `issue
tracker`_, contribution is always welcome, see :ref:`contributing`.

.. _issue tracker: https://github.com/flacjacket/pywayland/issues
.. _Wayland releases: https://wayland.freedesktop.org/releases.html
