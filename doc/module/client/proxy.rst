.. module:: pywayland.proxy

.. _client-proxy:

Proxy
=====

:class:`Proxy` objects are not created directly, and users should generally not
create a proxy class on their own.  Proxy classes give client side access to
the interfaces defined by the Wayland protocol (see :ref:`protocol`).  Proxies
are returned from the server after calling protocol methods which return
``new_id``'s.

.. autoclass:: pywayland.proxy.Proxy
   :members:
