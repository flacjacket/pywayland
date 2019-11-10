# Copyright 2019 Sean Vig
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

"""The core objects used by the protocol definitions

This defines the core objects that are used in building up the protocols and
interfaces.  Each interface has a set of requests and events that are
associated with it.  These functions are invoked from the corresponding proxy
and resource instances.
"""

from .argument import Argument, ArgumentType  # noqa: F401
from .globals import Global  # noqa: F401
from .interface import Interface  # noqa: F401
from .proxy import Proxy  # noqa: F401
from .resource import Resource  # noqa: F401
