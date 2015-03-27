.. module:: pywayland.scanner

.. _scanner-scanner:

Scanner
=======

Using the Scanner module
------------------------

The PyWayland scanner allows you to generate the protocol scanner output within
Python scripts.  The general procedure to invoke the scanner will be to make a
:class:`Scanner` object, scan the input file, and have the Scanner output to a
directory.  These steps are done as:

.. code-block:: python

    Scanner(path_to_xml_file)
    Scanner.scan()
    Scanner.output(path_to_output_dir)

See the definitions below for more information on using Scanner objects.

Scanner Module
--------------

.. autoclass:: pywayland.scanner.Scanner
   :members:
