# This file has been autogenerated by the pywayland scanner

# Copyright 2015 Sean Vig
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

from pywayland.protocol_core import Global, Interface, Proxy, Resource


class WlXfail(Interface):
    """Xfailing interface

    Items that do not really work yet are put in here, they should be moved
    once they shart working.
    """

    name = "wl_xfail"
    version = 1


class WlXfailProxy(Proxy[WlXfail]):
    interface = WlXfail


class WlXfailResource(Resource):
    interface = WlXfail


class WlXfailGlobal(Global):
    interface = WlXfail


WlXfail._gen_c()
WlXfail.proxy_class = WlXfailProxy
WlXfail.resource_class = WlXfailResource
WlXfail.global_class = WlXfailGlobal
