.. module:: pywayland.protocol_core.interface

.. _interface:

Interface Module
================

Interface Class
---------------

:class:`Interface` objects are only created as a subclass of Interface.  The
Interface class wraps the protocol objects, and serves to initialize a set of
parameters for the Interface and provide decorators for defining
:class:`~pywayland.interface.Message` objects on the interface.  See
:ref:`protocol` for more on the Wayland protocol objects.

.. autoclass:: pywayland.protocol_core.interface.Interface
   :members:

Interface Metaclass
-------------------

This metaclass initializes lists for the requests and events on an interface
and initializes a cdata struct for the class.

.. autoclass:: pywayland.protocol_core.interface.InterfaceMeta
   :members:

Message Module
==============

:class:`~pywayland.interface.Message` objects are used to wrap the method calls
on the protocol objects.  The Message objects are added to the
:class:`~pywayland.interface.Interface`'s as either requests (client-side
functions) or events (server-side functions).  See :ref:`protocol` for more
information.

.. automodule:: pywayland.protocol_core.interface.Message
    :members:
