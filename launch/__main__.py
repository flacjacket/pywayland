import array
import os
import select
import socket
import time

from ._ffi import ffi

lib = ffi.dlopen()


def handle_event(sock, fd):
    msg_size = ffi.sizeof("struct swc_launch_event")
    cmsg_size = ffi.sizeof("int")
    msg, ancdata, _, _ = sock.recvmsg(msg_size, socket.CMSG_LEN(cmsg_size))

    event = ffi.new("struct swc_launch_event *")
    ffi.memmove(event, msg, msg_size)

    if event.type == lib.SWC_LAUNCH_EVENT_RESPONSE:
        print("got serial:", event.serial)
    else:
        if event.type == lib.SWC_LAUNCH_EVENT_ACTIVATE:
            print("got activate")
        elif event.type == lib.SWC_LAUNCH_EVENT_DEACTIVATE:
            print("got deactivate")
        print("success:", event.success)


def send_request(sock, fd):
    request = ffi.new("struct swc_launch_request *")
    request.type = lib.SWC_LAUNCH_REQUEST_ACTIVATE_VT
    request.vt = 3

    msg = ffi.buffer(request)[:]
    sock.sendmsg([msg], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, array.array("i", [fd]))])


if __name__ == "__main__":
    fd = int(os.getenv("SWC_LAUNCH_SOCKET"))
    sock = socket.socket(socket.AF_UNIX, fileno=fd)

    start = time.time()
    while time.time() < start + 3:
        rlist, _, _ = select.select([fd], [], [], 0)
        if rlist:
            handle_event(sock, rlist[0])

    send_request(sock, fd)

    start = time.time()
    while time.time() < start + 3:
        rlist, _, _ = select.select([fd], [], [], 0)
        if rlist:
            handle_event(sock, rlist[0])
