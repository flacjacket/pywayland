.. module:: pywayland.protocol_core

.. _protocol_core:

Protocol Core Modules
=====================

.. toctree::
   :maxdepth: 2

Interface
---------

:class:`Interface` objects are only created as a subclass of Interface.  The
Interface class wraps the protocol objects, and serves to initialize a set of
parameters for the Interface and provide decorators for defining
:class:`Message` objects on the interface.

.. autoclass:: Interface
   :members:

Interface Metaclass
-------------------

This metaclass initializes lists for the requests and events on an interface
and initializes a cdata struct for the class.

.. autoclass:: pywayland.protocol_core.interface.InterfaceMeta
   :members:

Proxy
-----

:class:`Proxy` objects are not created directly, and users should generally not
create a proxy class on their own.  Proxy classes give client side access to
the interfaces defined by the Wayland protocol.  Proxies are returned from the
server after calling protocol methods which return ``new_id``'s.

.. autoclass:: Proxy
   :members:

Resource
--------

.. autoclass:: Resource
   :members:

Global
------

.. autoclass:: Global
   :members:

Message
-------

:class:`Message` objects are used to wrap the method calls
on the protocol objects.  The Message objects are added to the
:class:`Interface`'s as either requests (client-side
functions) or events (server-side functions).

.. autoclass:: Message
   :members:

Argument
--------

.. autoclass:: Argument
   :members:

ArgumentType
------------

.. autoclass:: ArgumentType
   :members:
