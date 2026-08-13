from collections.abc import Callable
from typing import Any, ParamSpec, Self, TypeVar, overload

class CData:
    def __getitem__(self, idx: int) -> Self: ...
    def __setitem__(self, idx: int, elem: Self) -> None: ...

# built-in cdata types
class CharCData(CData): ...

# extern functions
class DispatcherFunc: ...
class ResourceDestroyFunc: ...
class EventLoopFdFunc: ...
class EventLoopSignalFunc: ...
class EventLoopTimerFunc: ...
class EventLoopIdleFunc: ...
class GlobalBindFunc: ...
class NotifyFunc: ...

class WlArgument(CData):
    i: int
    u: int
    f: int
    s: CharCData
    o: WlObject
    n: int
    a: WlArray
    h: int

class WlArray(CData):
    size: int
    alloc: int
    data: CData

class WlClient(CData):
    pass

class WlDisplay(CData):
    pass

class WlEventLoop(CData):
    pass

class WlEventSource(CData):
    pass

class WlGlobal(CData):
    pass

class WlInterface(CData):
    name: CharCData
    version: int
    method_count: int
    methods: WlMessage
    event_count: int
    events: WlMessage

class WlList(CData):
    @property
    def prev(self) -> WlList: ...
    @property
    def next(self) -> WlList: ...

class WlListener(CData):
    link: WlList
    notify: NotifyFunc

class WlListenerContainer(CData):
    handle: CData
    destroy_listener: WlListener

class WlMessage(CData):
    name: CharCData
    signature: CharCData
    types: WlInterface

class WlObject(CData):
    pass

class WlProxy(CData):
    pass

class WlQueue(CData):
    pass

class WlResource(CData):
    pass

class WlSignal(CData):
    listener_list: WlList

# special types
P = ParamSpec("P")
R = TypeVar("R")
_CDataT = TypeVar("_CDataT", bound=CData)
_CDataO = TypeVar("_CDataO", bound=CData)

# Any type of CData
NULL: Any

def new(cdecl: str, init: Any = None) -> _CDataT: ...  # type: ignore [type-var]
@overload
def gc(
    cdata: _CDataT, destructor: Callable[[_CDataT], Any], size: int = 0
) -> _CDataT: ...
@overload
def gc(cdata: _CDataT, destructor: None, size: int = 0) -> None: ...
def buffer(cdata: _CDataT, size: int = -1) -> bytearray: ...
def string(cdata: CharCData, maxlen: int = -1) -> bytes: ...
def release(x: _CDataT) -> None: ...
def def_extern() -> Callable[[Callable[P, R]], Callable[P, R]]: ...
def new_handle(x: Any) -> _CDataT: ...  # type: ignore [type-var]
def from_handle(x: _CDataT) -> Any: ...
def cast(cdecl: str, source: _CDataT) -> _CDataO: ...  # type: ignore [type-var]
def addressof(cdata: _CDataT, *fields_or_indexes: str | int) -> _CDataT: ...
def offsetof(cdecl: str, *fields_or_indexes: str | int) -> int: ...
