Welcome to PyWayland's documentation!
=====================================

PyWayland provides Python bindings to the Wayland library, using pure Python by
making calls through the CFFI module.  PyWayland supports Python 2.7 and >=3.2,
including PyPy and PyPy 3.  This is currently a highly experimental package,
and the usage is likely to change between releases.  Check back as development
continues, contributions are always welcome!

Check out the different sections below for information on installing and
running PyWayland.  There is also information on running and developing from
source (feedback and contributions are always welcome on the `issue
tracker`_).  Finally, the module documentation is included.

.. _issue tracker: https://github.com/flacjacket/pywayland/issues

Documentation
-------------

.. toctree::
   :maxdepth: 2

   install
   contributing

Module Reference
----------------

Core Modules
^^^^^^^^^^^^

.. toctree::
   :maxdepth: 2

   module/interface
   module/message

Client and Server Modules
^^^^^^^^^^^^^^^^^^^^^^^^^

.. toctree::
   :maxdepth: 2

   module/client/index
   module/server/index

Scanner and Protocol Modules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. toctree::
   :maxdepth: 2

   scanner
   module/protocol/index
   module/scanner/index
