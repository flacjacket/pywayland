.. module:: pywayland.scanner

.. _scanner-scanner:

Scanner
=======

Using the Scanner module
------------------------

The PyWayland scanner allows you to generate the protocol scanner output within
Python scripts.  The general procedure to invoke the scanner will be to make a
:class:`Protocol` object, scan the input file, and have the Protocol output to a
directory.  These steps are done as:

.. code-block:: python

    Protocol.parse_file(path_to_xml_file)
    Protocol.output(path_to_output_dir, {})

See the definitions below for more information on using Protocol objects.

Protocol Module
---------------

.. autoclass:: pywayland.scanner.Protocol
   :members:
