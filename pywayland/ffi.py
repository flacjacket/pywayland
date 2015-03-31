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

from cffi import FFI

ffi = FFI()

ffi.cdef("""
/******************************************************************************
 * wayland-util.h
 *****************************************************************************/
// Structs for event and request dispactching
typedef int32_t wl_fixed_t;

struct wl_message {
    const char *name;
    const char *signature;
    const struct wl_interface **types;
};
struct wl_interface {
    const char *name;
    int version;
    int method_count;
    const struct wl_message *methods;
    int event_count;
    const struct wl_message *events;
};
union wl_argument {
    int32_t i; /**< signed integer */
    uint32_t u; /**< unsigned integer */
    wl_fixed_t f; /**< fixed point */
    const char *s; /**< string */
    struct wl_object *o; /**< object */
    uint32_t n; /**< new_id */
    struct wl_array *a; /**< array */
    int32_t h; /**< file descriptor */
};

typedef int (*wl_dispatcher_func_t)(const void *, void *, uint32_t,
                                    const struct wl_message *,
                                    union wl_argument *);
""")

C = ffi.verify("""
#include <wayland-client.h>
#include <wayland-server.h>
""", libraries=['wayland-client', 'wayland-server'], modulename='_pywayland')
