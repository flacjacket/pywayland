.. module:: pywayland.interface

.. _interface:

Interface Module
================

Interface Class
---------------

:class:`Interface` objects are only created as a subclass of Interface.  The
Interface class wraps the protocol objects, and serves to initialize a set of
parameters for the Interface and provide decorators for defining
:class:`~pywayland.message.Message` objects on the interface.  See
:ref:`protocol` for more on the Wayland protocol objects.

.. autoclass:: pywayland.interface.Interface
   :members:

Interface Metaclass
-------------------

This metaclass initializes lists for the requests and events on an interface
and initializes a cdata struct for the class.

.. autoclass:: pywayland.interface.InterfaceMeta
   :members:
