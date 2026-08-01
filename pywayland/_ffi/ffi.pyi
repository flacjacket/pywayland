from collections.abc import Callable
from typing import Any, Self, TypeVar, overload

class CData:
    def __getitem__(self, idx: int) -> Self: ...
    def __setitem__(self, idx: int, elem: Self) -> None: ...

# built-in cdata types
class CharCData(CData): ...
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
_FuncType = Callable[..., Any]
_F = TypeVar("_F", bound=_FuncType)
_CDataT = TypeVar("_CDataT", bound=CData)
_CDataO = TypeVar("_CDataO", bound=CData)

# Any type of CData
NULL: Any

@overload
def new(cdecl: str) -> _CDataT: ...  # type: ignore [type-var]
@overload
def new(cdecl: str, init: Any) -> _CDataT: ...  # type: ignore [type-var]
def gc(
    cdata: _CDataT, destructor: Callable[[_CDataT], None] | None, size: int = 0
) -> _CDataT: ...
def buffer(cdata: _CDataT, size: int = -1) -> bytearray: ...
def string(cdata: CharCData) -> bytes: ...
def release(cdata: _CDataT) -> None: ...
def def_extern() -> Callable[[_F], _F]: ...
def new_handle(self: Any) -> _CDataT: ...  # type: ignore [type-var]
def from_handle(cdata: _CDataT) -> Any: ...
def cast(new_type: str, cdata: _CDataT) -> _CDataO: ...  # type: ignore [type-var]
def addressof(cdata: _CDataT) -> _CDataT: ...
def offsetof(cdecl: str, offset: Any) -> int: ...
