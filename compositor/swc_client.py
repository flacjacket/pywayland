import array
import select
import socket

from ._ffi_launch import ffi, lib


class SwcClient(object):
    serial = 1

    def __init__(self, fd):
        self.fd = fd

        self.sock = socket.socket(socket.AF_UNIX, fileno=self.fd)

    def _send_request(self, request):
        """Send the swc_launch_request cdata"""
        request.serial = SwcClient.serial
        SwcClient.serial += 1

        msg = ffi.buffer(request)[:]
        cmsg = array.array("i", [self.fd])
        self.sock.sendmsg([msg], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, cmsg)])

        while True:
            rlist, _, _ = select.select([self.fd], [], [], 2)
            if rlist:
                event = self._recv_event()
                if event.type == lib.SWC_LAUNCH_EVENT_RESPONSE and event.serial == request.serial:
                    return event
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

        return event

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
        buf = ffi.new("char[]", ffi.sizeof("struct swc_launch_request *") + len(path) + 1)
        request = ffi.cast("struct swc_launch_request *", buf)
        request.type = lib.SWC_LAUNCH_REQUEST_OPEN_DEVICE
        request.flags = flags
        path = path.encode()

        ffi.memmove(request.path, path, len(path) + 1)

        event = self._send_request(request)
        print("request {}: opened fd {:d} to path {:s}".format(event.serial, event.fd, path))
        return event.fd

    def handle_data(self):
        """Read and handle all pending messages"""
        while True:
            rlist, _, _ = select.select([self.fd], [], [], 0)
            if not rlist:
                break
            event = self._recv_event()
            self._handle_event(event)
