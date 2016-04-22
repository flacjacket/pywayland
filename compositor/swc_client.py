import array
import itertools
import select
import socket
import struct

from ._ffi_launch import ffi, lib


class SwcClient(object):
    serial = 1

    def __init__(self, fd):
        self.fd = fd

        self.sock = socket.socket(socket.AF_UNIX, fileno=self.fd)

    def _send_request(self, buf):
        """Send the swc_launch_request cdata"""
        request = ffi.cast("struct swc_launch_request *", buf)
        request.serial = SwcClient.serial
        SwcClient.serial += 1

        msg = ffi.buffer(buf)[:]
        cmsg = array.array("i", [self.fd])
        self.sock.sendmsg([msg], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, cmsg)])

        while True:
            rlist, _, _ = select.select([self.fd], [], [], 2)
            if rlist:
                event, fds = self._recv_event()
                if event.type == lib.SWC_LAUNCH_EVENT_RESPONSE and event.serial == request.serial:
                    return fds
                self._handle_event(event)
                continue
            raise TimeoutError("Did not receive response from swc launcher")

    def _recv_event(self):
        """Read and return a swc_launch_event cdata"""
        msg_size = ffi.sizeof("struct swc_launch_event")
        cmsg_size = ffi.sizeof("int")
        msg, ancdata, _, _ = self.sock.recvmsg(msg_size, socket.CMSG_LEN(cmsg_size))

        event = ffi.new("struct swc_launch_event *")
        ffi.memmove(event, msg, msg_size)

        fds = list(itertools.chain.from_iterable(struct.unpack("i", cmsg_data) for _, _, cmsg_data in ancdata))

        return event, fds

    def _handle_event(self, event):
        if event.type == lib.SWC_LAUNCH_EVENT_ACTIVATE:
            print("event: activate")
        elif event.type == lib.SWC_LAUNCH_EVENT_DEACTIVATE:
            print("event: deactivate")
        else:
            print("event: UNKNOWN")

    def send_activate_vt(self, vt):
        """Send message to activate the given VT"""
        request = ffi.new("struct swc_launch_request *")
        request.type = lib.SWC_LAUNCH_REQUEST_ACTIVATE_VT
        request.vt = vt

        self._send_request(request)
        print("request {:d}: activate VT {:d}".format(request.serial, vt))

    def send_open_device(self, path, flags):
        """Send message to open fd to given path"""
        path_cdata = ffi.new("char[]", path.encode())

        buf = ffi.new("char[]", ffi.sizeof("struct swc_launch_request") + ffi.sizeof(path_cdata))
        request = ffi.cast("struct swc_launch_request *", buf)
        request.type = lib.SWC_LAUNCH_REQUEST_OPEN_DEVICE
        request.flags = flags

        ffi.memmove(request + 1, path_cdata, ffi.sizeof(path_cdata))

        fds = self._send_request(buf)
        if not fds:
            print("request {:d}: Unable to open {:s}".format(request.serial, path))
            return
        fd = fds[0]
        print("request {}: opened fd {:d} to path {:s}".format(request.serial, fd, path))
        return fd

    def handle_data(self):
        """Read and handle all pending messages"""
        while True:
            rlist, _, _ = select.select([self.fd], [], [], 0)
            if not rlist:
                break
            event, _ = self._recv_event()
            self._handle_event(event)
