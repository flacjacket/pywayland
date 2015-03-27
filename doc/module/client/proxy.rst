.. module:: pywayland.client.proxy

.. _client-proxy:

Proxy
=====

Proxy Class
-----------

:class:`Proxy` objects are not created directly, and users should generally not
create a proxy class on their own.  Proxy classes give client side access to
the interfaces defined by the Wayland protocol (see :ref:`protocol`).  Proxies
are returned from the server after calling protocol methods which return
``new_id``'s.

.. autoclass:: pywayland.client.proxy.Proxy
   :members:

Proxy Metaclass
---------------

The :class:`ProxyMeta` is a metaclass that constructs proxy objects based on a
protocol interface.  This is used to construct the proxies with the appropriate
parameters.

.. autoclass:: pywayland.client.proxy.ProxyMeta
   :members:
