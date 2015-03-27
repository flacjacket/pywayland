.. _pywayland-scanner:

PyWayland Scanner
=================

The PyWayland scanner parses the ``wayland.xml`` protocol definition file and
outputs interfaces with the events, requests, and enums defined by the
protocol.  See :ref:`scanner` for details on the scanner implementation.

Command-line Invocation
-----------------------

If you have installed PyWayland, the scanner is placed in your path as
``pywayland-scanner.py``.  By default, invoking the scanner reads in the XML
file from ``/usr/share/wayland/wayland.xml`` and outputs the protocol
definitions to ``./protocol/``.

If you are running PyWayland from source, you can use the scanner in
``./bin/pywayland-scanner.py``.  This file sets the path to the current source
directory and runs method used by the entry-point.  Otherwise, this functions
the same as above.

Script Invocation
-----------------

In addition to the command-line use, you can use the scanner from within Python
scripts.  This is done, for example, when installing or building the docs to
ensure the protocol modules are included in both.  For details on invoking the
scanner module, see :class:`~pywayland.scanner.Scanner`.
