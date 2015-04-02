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

from pywayland import C


class EventQueue(object):
    """A queue for wl_proxy object events.

    Event queues allows the events on a display to be handled in a thread-safe
    manner. See :class:`~pywayland.client.Display` for details.
    """
    def __init__(self, display):
        self._ptr = C.wl_display_create_queue(display._ptr)
