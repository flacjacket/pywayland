from collections.abc import Callable
from typing import Any, Self, TypeVar, overload

class CData:
    def __getitem__(self, idx: int) -> Self: ...
    def __setitem__(self, idx: int, elem: Self) -> None: ...

class DispatcherFuncT: ...
class ResourceDestroyFuncT: ...
class EventLoopFdFuncT: ...
class EventLoopSignalFuncT: ...
class EventLoopTimerFuncT: ...
class EventLoopIdleFuncT: ...
class GlobalBindFuncT: ...
class NotifyFuncT: ...

# built-in cdata types
class CharCData(CData): ...

# wayland cdata types
class WlArgumentCData(CData):
    i: int
    u: int
    f: int
    s: CharCData
    o: WlObjectCData
    n: int
    a: WlArrayCData
    h: int

class WlArrayCData(CData):
    size: int
    alloc: int
    data: CData

class WlClientCData(CData): ...
class WlDisplayCData(CData): ...
class WlEventLoopCData(CData): ...
class WlEventSourceCData(CData): ...
class WlGlobalCData(CData): ...

class WlInterfaceCData(CData):
    name: CharCData
    version: int
    method_count: int
    methods: WlMessageCData
    event_count: int
    events: WlMessageCData

class WlListCData(CData):
    @property
    def prev(self) -> WlListCData: ...
    @property
    def next(self) -> WlListCData: ...

class WlListenerCData(CData):
    link: WlListCData
    notify: NotifyFuncT

class WlListenerContainerCData(CData):
    handle: CData
    destroy_listener: WlListenerCData

class WlMessageCData(CData):
    name: CharCData
    signature: CharCData
    types: WlInterfaceCData

class WlObjectCData(CData): ...
class WlProxyCData(CData): ...
class WlQueueCData(CData): ...
class WlResourceCData(CData): ...

class WlSignalCData(CData):
    listener_list: WlListCData

# special types
_FuncType = Callable[..., Any]
_F = TypeVar("_F", bound=_FuncType)
_CDataT = TypeVar("_CDataT", bound=CData)
_CDataO = TypeVar("_CDataO", bound=CData)

# Any type of CData
NULL: Any

@overload
def new(cdecl: str) -> _CDataT: ...  # type: ignore [type-var, misc]
@overload
def new(cdecl: str, init: Any) -> _CDataT: ...  # type: ignore [type-var, misc]
def gc(
    cdata: _CDataT, destructor: None | Callable[[_CDataT], None], size: int = 0
) -> _CDataT: ...
def buffer(cdata: _CDataT, size: int = -1) -> bytearray: ...
def string(cdata: CharCData) -> bytes: ...
def release(cdata: _CDataT) -> None: ...
def def_extern() -> Callable[[_F], _F]: ...
def new_handle(self: Any) -> _CDataT: ...  # type: ignore [type-var, misc]
def from_handle(cdata: _CDataT) -> Any: ...
def cast(new_type: str, cdata: _CDataT) -> _CDataO: ...  # type: ignore [type-var, misc]
def addressof(cdata: _CDataT) -> _CDataT: ...
def offsetof(cdecl: str, offset: Any) -> int: ...
