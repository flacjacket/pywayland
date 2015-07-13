from __future__ import print_function

import fcntl
import functools
import os
import signal
import sys

import logging

from ._ffi_launcher import ffi
from ._ffi_launcher.lib import (
    TTY_MAJOR, KDGKBMODE, KDSKBMODE, KDSETMODE, KDGETMODE, K_OFF, KD_GRAPHICS,
    VT_SETMODE, VT_AUTO, VT_PROCESS, VT_ACKACQ, VT_RELDISP, VT_ACTIVATE
)

logging.basicConfig(filename='output.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logger = logging.getLogger('launcher')


def handle_chld(launcher, signum, stack):
    _, status = os.wait()
    logger.info('Server exited with status %d', os.WEXITSTATUS(status))
    # TODO: figure out how to run/kill the launcher... asyncio event loop maybe? or wayland event loop?


def handle_usr1(launcher, signum, stack):
    # TODO: send deactivate...
    fcntl.ioctl(launcher.tty_fd, VT_RELDISP, 1)
    logger.info("launcher: USR1 handler run")


def handle_usr2(launcher, signum, stack):
    fcntl.ioctl(launcher.tty_fd, VT_RELDISP, VT_ACKACQ)
    logger.info("launcher: USR2 handler run")
    # TODO: send activate...


class Launcher(object):
    def __init__(self, tty=None):
        self.tty = tty
        self.tty_fd = None
        self.kbmode = None
        self.mode = None

    def __enter__(self):
        tty = sys.stdin.fileno() if self.tty is None else self.tty
        logger.info("launcher: running on VT %d", tty)

        # setup signals
        signal.signal(signal.SIGUSR1, functools.partial(handle_usr1, self))
        signal.signal(signal.SIGUSR2, functools.partial(handle_usr2, self))

        # setup tty
        stat = os.fstat(tty)
        if os.major(stat.st_rdev) != TTY_MAJOR or os.minor(stat.st_rdev) == 0:
            logger.exception("launcher must be run from a virtual terminal")
            raise RuntimeError
        self.tty_fd = tty

        buf = bytearray(1)

        if fcntl.ioctl(tty, KDGKBMODE, buf):
            logger.exception("failed to get KDGKBMODE")
            raise RuntimeError
        if fcntl.ioctl(tty, KDSKBMODE, K_OFF):
            logger.exception("failed to set K_OFF keyboard mode")
            raise RuntimeError
        self.kbmode = buf[0]

        if fcntl.ioctl(tty, KDGETMODE, buf):
            logger.exception("failed to get text/graphics mode")
            self.finalize()
            raise RuntimeError
        if fcntl.ioctl(tty, KDSETMODE, KD_GRAPHICS):
            logger.exception("unable to set KD_GRAPHICS on tty")
            self.finalize()
            raise RuntimeError
        self.mode = buf[0]

        mode = ffi.new('struct vt_mode *')
        mode.mode = chr(VT_PROCESS).encode()
        mode.relsig = signal.SIGUSR1
        mode.acqsig = signal.SIGUSR2
        if fcntl.ioctl(tty, VT_SETMODE, bytes(ffi.buffer(mode))) == -1:
            logger.exception("unable to set VT mode")
            self.finalize()
            raise RuntimeError

        logger.info('launcher: setup done')

        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if self.tty_fd is None:
            return

        # reset VT mode
        mode = ffi.new('struct vt_mode *')
        mode.mode = chr(VT_AUTO).encode()
        if fcntl.ioctl(self.tty_fd, VT_SETMODE, bytes(ffi.buffer(mode))) == -1:
            logger.exception("Failed to reset VT mode")

        # reset keyboard
        if self.kbmode is not None and fcntl.ioctl(self.tty_fd, KDSKBMODE, self.kbmode):
            logger.exception("Failed to reset keyboard mode")
        self.kbmode = None

        # reset graphics
        if self.mode is not None and fcntl.ioctl(self.tty_fd, KDSETMODE, self.mode):
            logger.exception("Failed to reset graphics")
        self.mode = None

        self.tty_fd = None

        logger.info('launcher: finalize done')

    def activate_vt(self, vt):
        fcntl.ioctl(self.tty_fd, VT_ACTIVATE, vt)
