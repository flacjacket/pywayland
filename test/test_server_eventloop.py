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

from pywayland.server.eventloop import EventLoop
from pywayland.server.listener import Listener

import os
import signal
import time


class _GetCallback(object):
    def __init__(self):
        self.callback = None
        self.n_calls = 0


def _fd_callback(fd, mask, data):
    data.callback = fd
    data.n_calls += 1
    return 0


def _signal_callback(signal_number, data):
    data.callback = signal_number
    data.n_calls += 1
    return 1


def _timer_callback(data):
    data.n_calls += 1
    return 1


def test_event_loop_post_dispatch_check():
    callback = _GetCallback()
    event_loop = EventLoop()

    r, w = os.pipe()

    try:
        source = event_loop.add_fd(r, _fd_callback, EventLoop.FdMask.WL_EVENT_READABLE, callback)
        source.check()

        event_loop.dispatch(0)
        assert callback.callback == r
    finally:
        os.close(r)
        os.close(w)


def test_event_loop_signal():
    callback = _GetCallback()
    event_loop = EventLoop()

    event_loop.add_signal(signal.SIGUSR1, _signal_callback, callback)

    event_loop.dispatch(0)
    assert callback.callback is None

    os.kill(os.getpid(), signal.SIGUSR1)

    event_loop.dispatch(0)
    assert callback.callback == signal.SIGUSR1


def test_event_loop_multiple_same_signals():
    callback = _GetCallback()
    event_loop = EventLoop()

    signal_rm = event_loop.add_signal(signal.SIGUSR1, _signal_callback, callback)
    event_loop.add_signal(signal.SIGUSR1, _signal_callback, callback)

    event_loop.dispatch(0)
    assert callback.n_calls == 0

    # Check callback gets 2 calls
    for _ in range(5):
        callback.n_calls = 0
        os.kill(os.getpid(), signal.SIGUSR1)
        event_loop.dispatch(0)

        assert callback.n_calls == 2

    # Remove one of the signals
    signal_rm.remove()

    # Callback only gets call now
    for _ in range(5):
        callback.n_calls = 0
        os.kill(os.getpid(), signal.SIGUSR1)
        event_loop.dispatch(0)

        assert callback.n_calls == 1


def test_event_loop_timer():
    callback = _GetCallback()
    event_loop = EventLoop()

    source = event_loop.add_timer(_timer_callback, callback)
    source.timer_update(10)

    event_loop.dispatch(0)
    assert callback.n_calls == 0

    event_loop.dispatch(20)
    assert callback.n_calls == 1


def _timer_update_callback1(data):
    data.n_calls += 1
    data.source2.timer_update(1000)
    return 1


def _timer_update_callback2(data):
    data.n_calls += 1
    data.source1.timer_update(1000)
    return 1


def test_event_loop_timer_updates():
    callback = _GetCallback()
    event_loop = EventLoop()

    source1 = event_loop.add_timer(_timer_update_callback1, callback)
    source1.timer_update(10)

    source2 = event_loop.add_timer(_timer_update_callback2, callback)
    source2.timer_update(10)

    callback.source1 = source1
    callback.source2 = source2

    assert callback.n_calls == 0

    # Wait 15 ms, so both timers should be called when we dispatch
    time.sleep(0.015)

    # This should take < 1 sec
    start_time = time.time()
    event_loop.dispatch(20)
    end_time = time.time()

    assert callback.n_calls == 2

    assert end_time - start_time < 1


def _destroy_notify_a(listener, data):
    global a
    a = True


def _destroy_notify_b(listener, data):
    global b
    b = True


def test_event_loop_destroy():
    global a, b
    a = False
    b = False

    event_loop = EventLoop()
    listener_a = Listener(_destroy_notify_a)
    listener_b = Listener(_destroy_notify_b)

    event_loop.add_destroy_listener(listener_a)
    event_loop.add_destroy_listener(listener_b)

    listener_a.remove()

    event_loop.destroy()

    import gc
    gc.collect()

    assert a is False
    assert b is True
