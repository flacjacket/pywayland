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
to use the most `recent version of Wayland available
<http://wayland.freedesktop.org/releases.html>`_, and the pip package will try
to track the most recent version.

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
cffi_ (to perform Wayland library calls) and six_ (to facilitate cross-version
compatibility), both of which can be pip installed.  Note that PyPy platforms
ship with cffi, however, PyWayland currently requires cffi >= 1.0.0, which will
not ship in PyPy until 2.6, which is unreleased as of this writing.

Furthermore, versions of Python 2 and Python <=3.3 require enum34_ (for support
for :pep:`435`-style ``Enum``'s), this can be pip installed.

.. _cffi: https://cffi.readthedocs.org/en/latest/
.. _enum34: https://pypi.python.org/pypi/enum34/
.. _six: https://pythonhosted.org/six/

Generating the Wayland Protocol
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

At this point, you have the base PyWayland module, which contains some core
objects and objects specific to client and server implementations.  The client
and server exchange messages defined in the Wayland protocol, which is an XML
file that ships with Wayland.  The scanner parses this XML file and generates
the relevant objects.

If the Wayland protocol file is in the default location
(``/usr/share/wayland/wayland.xml``), you should be able to build the protocol
files without any problems::

    $ python setup.py generate_protocol

This will output the protocol files to the directory ``./pywayland/protocol/``.
The input file and the output directory can be set from the command line
options, see ``python setup.py generate_protocol -h`` for more information.


Building cffi Module
^^^^^^^^^^^^^^^^^^^^

Once the protocol files are created, you can generate the cffi module.  If
libwayland is correctly installed, you will just need to run::

    $ python setup.py build_ext --inplace

Running PyWayland
^^^^^^^^^^^^^^^^^

At this point, you should be able to use the PyWayland library.  You can check
that you have everything installed correctly by running the associated
test-suite (note that you will also need ``pytest`` to run the tests).  Simply
run::

    $ py.tests

from the root directory.

If you have any problems or have any feedback, please report back to the `issue
tracker`_, contribution is always welcome, see :ref:`contributing`.

.. _issue tracker: https://github.com/flacjacket/pywayland/issues
