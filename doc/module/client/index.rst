.. _client:

Client Modules
==============

The base set of objects used by Wayland clients.  Users should only be
directly creating :class:`~pywayland.client.Display` and
:class:`~pywayland.client.EventQueue` objects.  The
:class:`~pywayland.client.proxy.Proxy` objects to interfaces should be returned
by making request calls.

.. toctree::
   :maxdepth: 2

   display
   eventqueue
   proxy
