.. module:: pywayland.client

.. _client:

Client Modules
==============

The base set of objects used by Wayland clients.  Users should only be
directly creating :class:`Display` and :class:`EventQueue` objects. The
:class:`~pywayland.protocol_core.Proxy` objects to interfaces should be returned
by making request calls.

Display
-------

.. autoclass:: Display
   :members:

EventQueue
----------

.. autoclass:: EventQueue
   :members:
