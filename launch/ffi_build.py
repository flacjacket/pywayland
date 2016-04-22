from cffi import FFI

ffi = FFI()

swc_defs = """
struct swc_launch_request {
    enum {
        SWC_LAUNCH_REQUEST_OPEN_DEVICE,
        SWC_LAUNCH_REQUEST_ACTIVATE_VT,
    } type;

    uint32_t serial;

    union {
        struct /* OPEN_DEVICE */
        {
            int flags;
            char path[0];
        };
        struct /* ACTIVATE_VT */
        {
            unsigned vt;
        };
    };
};

struct swc_launch_event {
    enum {
        SWC_LAUNCH_EVENT_RESPONSE,
        SWC_LAUNCH_EVENT_ACTIVATE,
        SWC_LAUNCH_EVENT_DEACTIVATE,
    } type;

    union {
        struct /* RESPONSE */
        {
            uint32_t serial;
            bool success;
        };
    };
};"""

ffi.set_source("launch._ffi", "#include <stdbool.h>" + swc_defs)
ffi.cdef(swc_defs)

if __name__ == "__main__":
    ffi.compile()
