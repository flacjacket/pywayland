"""
Test against issue <https://github.com/flacjacket/pywayland/issues/61>
"""

from pywayland.server import Listener, Signal


def test_ref_removal():

    def callback(*_):
        pass

    sig = Signal()
    listener = Listener(callback)
    assert listener._ptr is not None
    assert listener._notify is not None
    assert listener._signal is None
    assert not sig._link
    sig.add(listener)
    assert len(sig._link) == 1
    assert listener._signal == sig
    listener.remove()
    assert len(sig._link) == 0
    assert listener._signal is None
    assert listener._notify is None
    assert listener._ptr is None


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
