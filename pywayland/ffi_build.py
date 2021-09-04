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


###############################################################################
# wayland-version.h
###############################################################################
CDEF = """
#define WAYLAND_VERSION_MAJOR ...
#define WAYLAND_VERSION_MINOR ...
#define WAYLAND_VERSION_MICRO ...
 """

###############################################################################
# wayland-util.h
###############################################################################
# wl_fixed_t handling
CDEF += """
typedef int32_t wl_fixed_t;
static inline double wl_fixed_to_double(wl_fixed_t f);
static inline wl_fixed_t wl_fixed_from_double(double d);
static inline wl_fixed_t wl_fixed_from_int(int i);
"""

# Event/request dispatching structs
CDEF += """
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
"""

# wl_array methods
CDEF += """
struct wl_array {
    size_t size;
    size_t alloc;
    void *data;
};
"""

# wl_list methods
CDEF += """
struct wl_list {
    struct wl_list *prev;
    struct wl_list *next;
};

void wl_list_remove(struct wl_list *elm);
int wl_list_empty(const struct wl_list *list);
"""

# Dispatcher callback
CDEF += """
typedef int (*wl_dispatcher_func_t)(const void *, void *, uint32_t,
                                    const struct wl_message *,
                                    union wl_argument *);
"""

###############################################################################
# wayland-client.h
###############################################################################
# wl_eventqueue methods
CDEF += """
void wl_event_queue_destroy(struct wl_event_queue *queue);
"""

# wl_proxy methods
CDEF += """
void wl_proxy_marshal_array(struct wl_proxy *p, uint32_t opcode,
                            union wl_argument *args);
struct wl_proxy *wl_proxy_create(struct wl_proxy *factory,
                                 const struct wl_interface *interface);
struct wl_proxy *
wl_proxy_marshal_array_constructor(struct wl_proxy *proxy,
                                   uint32_t opcode, union wl_argument *args,
                                   const struct wl_interface *interface);

void wl_proxy_destroy(struct wl_proxy *proxy);
int wl_proxy_add_dispatcher(struct wl_proxy *proxy,
                            wl_dispatcher_func_t dispatcher_func,
                            const void * dispatcher_data, void *data);
void wl_proxy_set_user_data(struct wl_proxy *proxy, void *user_data);
void *wl_proxy_get_user_data(struct wl_proxy *proxy);
"""

# wl_display methods
CDEF += """
struct wl_display* wl_display_connect(const char *name);
struct wl_display* wl_display_connect_to_fd(int fd);
void wl_display_disconnect(struct wl_display *display);
int wl_display_get_fd(struct wl_display *display);
int wl_display_dispatch(struct wl_display *display);
int wl_display_dispatch_pending(struct wl_display *display);
int wl_display_dispatch_queue(struct wl_display *display,
                              struct wl_event_queue *queue);
int wl_display_dispatch_queue_pending(struct wl_display *display,
                                      struct wl_event_queue *queue);
int wl_display_roundtrip(struct wl_display *display);
int wl_display_roundtrip_queue(struct wl_display *display,
                               struct wl_event_queue *queue);
int wl_display_get_error(struct wl_display *display);
int wl_display_read_events(struct wl_display *display);
int wl_display_prepare_read(struct wl_display *display);
int wl_display_prepare_read_queue(struct wl_display *display,
                                  struct wl_event_queue *queue);
int wl_display_flush(struct wl_display *display);
struct wl_event_queue *wl_display_create_queue(struct wl_display *display);
"""

###############################################################################
# wayland-server.h
###############################################################################
# wl_eventloop enum
CDEF += """
enum {
    WL_EVENT_READABLE = ...,
    WL_EVENT_WRITABLE = ...,
    WL_EVENT_HANGUP = ...,
    WL_EVENT_ERROR = ...
};
"""

# wl_listener struct
CDEF += """
typedef void (*wl_notify_func_t)(struct wl_listener *listener, void *data);
struct wl_listener {
    struct wl_list link;
    wl_notify_func_t notify;
};
"""

CDEF += """
struct wl_signal {
    struct wl_list listener_list;
};

void wl_signal_add(struct wl_signal *signal, struct wl_listener *listener);
void wl_signal_emit(struct wl_signal *signal, void *data);
"""

# wl_eventloop callbacks and methods
CDEF += """
typedef int (*wl_event_loop_fd_func_t)(int fd, uint32_t mask, void *data);
typedef int (*wl_event_loop_timer_func_t)(void *data);
typedef int (*wl_event_loop_signal_func_t)(int signal_number, void *data);
typedef void (*wl_event_loop_idle_func_t)(void *data);

void wl_event_loop_add_destroy_listener(struct wl_event_loop *loop,
                                        struct wl_listener * listener);

struct wl_event_loop *wl_event_loop_create(void);
void wl_event_loop_destroy(struct wl_event_loop *loop);
struct wl_event_source *wl_event_loop_add_fd(struct wl_event_loop *loop,
                                             int fd, uint32_t mask,
                                             wl_event_loop_fd_func_t func,
                                             void *data);
int wl_event_source_fd_update(struct wl_event_source *source, uint32_t mask);
struct wl_event_source *wl_event_loop_add_timer(struct wl_event_loop *loop,
                                                wl_event_loop_timer_func_t func,
                                                void *data);
struct wl_event_source *
wl_event_loop_add_signal(struct wl_event_loop *loop,
                         int signal_number,
                         wl_event_loop_signal_func_t func,
                         void *data);

int wl_event_loop_dispatch(struct wl_event_loop *loop, int timeout);
void wl_event_loop_dispatch_idle(struct wl_event_loop *loop);
struct wl_event_source *wl_event_loop_add_idle(struct wl_event_loop *loop,
                                               wl_event_loop_idle_func_t func,
                                               void *data);
int wl_event_loop_get_fd(struct wl_event_loop *loop);
"""

# wl_event_source methods
CDEF += """
int wl_event_source_timer_update(struct wl_event_source *source,
                                 int ms_delay);
int wl_event_source_remove(struct wl_event_source *source);
void wl_event_source_check(struct wl_event_source *source);
"""

# wl_display methods
CDEF += """
struct wl_display * wl_display_create(void);
void wl_display_destroy(struct wl_display *display);
struct wl_event_loop *wl_display_get_event_loop(struct wl_display *display);
int wl_display_add_socket(struct wl_display *display, const char *name);
const char *wl_display_add_socket_auto(struct wl_display *display);
void wl_display_terminate(struct wl_display *display);
void wl_display_run(struct wl_display *display);

uint32_t wl_display_get_serial(struct wl_display *display);
uint32_t wl_display_next_serial(struct wl_display *display);
void wl_display_destroy_clients(struct wl_display *display);
void wl_display_flush_clients(struct wl_display *display);

int wl_display_init_shm(struct wl_display *display);
uint32_t *wl_display_add_shm_format(struct wl_display *display, uint32_t format);
"""

# wl_global methods
CDEF += """
typedef void (*wl_global_bind_func_t)(struct wl_client *client, void *data,
                                      uint32_t version, uint32_t id);
struct wl_global *wl_global_create(struct wl_display *display,
                                   const struct wl_interface *interface,
                                   int version,
                                   void *data, wl_global_bind_func_t bind);
void wl_global_destroy(struct wl_global *global);
"""

# wl_client methods
CDEF += """
struct wl_client;
struct wl_client *wl_client_create(struct wl_display *display, int fd);
void wl_client_destroy(struct wl_client *client);
void wl_client_flush(struct wl_client *client);

typedef int pid_t;
typedef unsigned int uid_t;
typedef unsigned int gid_t;
void wl_client_get_credentials(struct wl_client *client,
    pid_t *pid, uid_t *uid, gid_t *gid);

void wl_client_add_destroy_listener(struct wl_client *client,
                                    struct wl_listener *listener);

struct wl_resource *
wl_client_get_object(struct wl_client *client, uint32_t id);
"""

# wl_resource methods
CDEF += """
typedef void (*wl_resource_destroy_func_t)(struct wl_resource *resource);

void wl_resource_post_event_array(struct wl_resource *resource,
                                  uint32_t opcode, union wl_argument *args);

void wl_resource_post_error(struct wl_resource *resource,
                            uint32_t code, const char *msg, ...);

struct wl_resource *
wl_resource_create(struct wl_client *client,
                   const struct wl_interface *interface,
                   int version, uint32_t id);
void
wl_resource_set_dispatcher(struct wl_resource *resource,
                           wl_dispatcher_func_t dispatcher,
                           const void *implementation,
                           void *data,
                           wl_resource_destroy_func_t destroy);

void
wl_resource_destroy(struct wl_resource *resource);
uint32_t
wl_resource_get_id(struct wl_resource *resource);
void *
wl_resource_get_user_data(struct wl_resource *resource);
int
wl_resource_get_version(struct wl_resource *resource);

void
wl_resource_add_destroy_listener(struct wl_resource *resource,
                                 struct wl_listener * listener);
"""

# anonymous file methods (from Weston)
CDEF += """
int
os_create_anonymous_file(int size);
"""

# cffi callback functions
CDEF += """
extern "Python" int dispatcher_func(const void *, void *, uint32_t, const struct wl_message *, union wl_argument *);
extern "Python" void resource_destroy_func(struct wl_resource *);
extern "Python" int event_loop_fd_func(int, uint32_t, void *);
extern "Python" int event_loop_signal_func(int, void *);
extern "Python" int event_loop_timer_func(void *);
extern "Python" void event_loop_idle_func(void *);
extern "Python" void global_bind_func(struct wl_client *, void *, uint32_t, uint32_t);
extern "Python" void notify_func(struct wl_listener *, void *);

struct wl_listener_container {
    void *handle;
    struct wl_listener destroy_listener;
};
"""

SOURCE = """
#include <wayland-client-core.h>
#include <wayland-server-core.h>
#include <wayland-version.h>

#include <fcntl.h>
#include <errno.h>
#include <sys/types.h>
"""

SOURCE += """
struct wl_listener_container {
    void *handle;
    struct wl_listener destroy_listener;
};
"""

SOURCE += """
/* This code is taken from Weston (MIT licensed) to provide access to anonymous
 * files with CLOEXEC set
 * Copyright (c) 2012 Collabora, Ltd.
 * http://cgit.freedesktop.org/wayland/weston/tree/shared/os-compatibility.c?id=1.8.0
 */

static int
set_cloexec_or_close(int fd)
{
    long flags;

    if (fd == -1)
        return -1;

    flags = fcntl(fd, F_GETFD);
    if (flags == -1)
        goto err;

    if (fcntl(fd, F_SETFD, flags | FD_CLOEXEC) == -1)
        goto err;

    return fd;

err:
    close(fd);
    return -1;
}

static int
create_tmpfile_cloexec(char *tmpname)
{
    int fd;

#ifdef HAVE_MKOSTEMP
    fd = mkostemp(tmpname, O_CLOEXEC);
    if (fd >= 0)
        unlink(tmpname);
#else
    fd = mkstemp(tmpname);
    if (fd >= 0) {
        fd = set_cloexec_or_close(fd);
        unlink(tmpname);
    }
#endif

    return fd;
}

int
os_create_anonymous_file(off_t size)
{
    static const char template[] = "/weston-shared-XXXXXX";
    const char *path;
    char *name;
    int fd;
    int ret;

    path = getenv("XDG_RUNTIME_DIR");
    if (!path) {
        errno = ENOENT;
        return -1;
    }

    name = malloc(strlen(path) + sizeof(template));
    if (!name)
        return -1;

    strcpy(name, path);
    strcat(name, template);

    fd = create_tmpfile_cloexec(name);

    free(name);

    if (fd < 0)
        return -1;

#ifdef HAVE_POSIX_FALLOCATE
    ret = posix_fallocate(fd, 0, size);
    if (ret != 0) {
        close(fd);
        errno = ret;
        return -1;
    }
#else
    ret = ftruncate(fd, size);
    if (ret < 0) {
        close(fd);
        return -1;
    }
#endif

    return fd;
}
"""

ffi_builder = FFI()
ffi_builder.set_source(
    "pywayland._ffi", SOURCE, libraries=["wayland-client", "wayland-server"]
)
ffi_builder.cdef(CDEF)


if __name__ == "__main__":
    ffi_builder.compile()
