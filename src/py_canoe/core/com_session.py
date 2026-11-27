"""Private STA executor used to centralize CANoe COM ownership."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from concurrent.futures import Future
from dataclasses import dataclass
from queue import Empty, Queue
from threading import Event, Lock, Thread, get_ident
from typing import Literal, TypeVar, cast
from uuid import UUID, uuid4

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class ComObjectHandle:
    """Opaque reference to a COM object owned by one live session."""

    session_id: UUID
    object_id: int
    generation: int


@dataclass(frozen=True, slots=True)
class ComMethodHandle:
    session_id: UUID
    object_id: int
    generation: int
    name: str


@dataclass(frozen=True, slots=True)
class ComEventSinkHandle:
    session_id: UUID
    sink_id: int


@dataclass(frozen=True, slots=True)
class ComIteratorHandle:
    session_id: UUID
    iterator_id: int
    generation: int


@dataclass(frozen=True, slots=True)
class _EventMethodHandle:
    event_sink: ComEventSinkHandle
    name: str


_ITERATION_END = object()


@dataclass(slots=True)
class _RegisteredObject:
    value: object
    identity: object


@dataclass(slots=True)
class _WorkItem:
    callback: Callable[..., object]
    args: tuple[object, ...]
    kwargs: dict[str, object]
    future: Future[object]


class ComSessionClosedError(RuntimeError):
    """Raised when work is submitted to a closed COM session."""


class ComSession:
    """Run COM work on one STA thread and pump its message queue while idle.

    Raw COM objects returned from callbacks are replaced with registry handles.
    """

    def __init__(self) -> None:
        self._queue: Queue[_WorkItem | None] = Queue()
        self._ready = Event()
        self._state_lock = Lock()
        self._worker_id: int | None = None
        self._startup_error: BaseException | None = None
        self._worker_error: BaseException | None = None
        self._shutdown_error: BaseException | None = None
        self._session_id = uuid4()
        self._generation = 0
        self._next_object_id = 1
        self._objects: dict[int, _RegisteredObject] = {}
        self._iterators: dict[int, Iterator[object]] = {}
        self._event_sinks: dict[int, object] = {}
        self._next_iterator_id = 1
        self._next_event_sink_id = 1
        self._closing = False
        self._closed = False
        self._abandon_event_sinks_on_shutdown = False
        self._thread = Thread(
            target=self._run,
            name="py-canoe-sta",
            daemon=True,
        )
        self._thread.start()
        self._ready.wait()
        if self._startup_error is not None:
            raise self._startup_error

    def invoke(
        self, callback: Callable[..., T], /, *args: object, **kwargs: object
    ) -> T:
        """Synchronously execute a callback on the owning STA.

        COM arguments must be passed as session-owned proxies, never raw objects.
        """
        if get_ident() == self._worker_id:
            self._raise_if_unavailable()
            return cast(T, self._execute(callback, args, kwargs))

        future: Future[object] = Future()
        item = _WorkItem(callback, args, kwargs, future)
        with self._state_lock:
            self._raise_if_unavailable()
            self._queue.put(item)
        return cast(T, future.result())

    def release(self, handle: ComObjectHandle) -> None:
        """Release one registered COM reference on the owning STA."""
        self.invoke(lambda: self._release_object(handle))

    def invalidate(
        self, *preserve: ComObjectHandle
    ) -> tuple[ComObjectHandle, ...]:
        """Invalidate the generation, optionally reissuing handles for root objects."""
        return cast(
            tuple[ComObjectHandle, ...],
            self.invoke(lambda: self._invalidate_objects(preserve)),
        )

    def get_attribute(self, handle: ComObjectHandle, name: str) -> object:
        return self.invoke(lambda: self._get_attribute(handle, name))

    def set_attribute(self, handle: ComObjectHandle, name: str, value: object) -> None:
        self.invoke(
            lambda resolved: setattr(self._resolve_handle(handle), name, resolved),
            value,
        )

    def call_object(
        self,
        handle: ComObjectHandle,
        args: tuple[object, ...],
        kwargs: dict[str, object],
    ) -> object:
        return self.invoke(
            lambda *resolved_args, **resolved_kwargs: self._resolve_handle(handle)(
                *resolved_args, **resolved_kwargs
            ),
            *args,
            **kwargs,
        )

    def call_method(
        self,
        method: ComMethodHandle,
        args: tuple[object, ...],
        kwargs: dict[str, object],
    ) -> object:
        return self.invoke(
            lambda *resolved_args, **resolved_kwargs: getattr(
                self._resolve_handle(
                    ComObjectHandle(
                        method.session_id, method.object_id, method.generation
                    )
                ),
                method.name,
            )(*resolved_args, **resolved_kwargs),
            *args,
            **kwargs,
        )

    def attach_events(
        self, handle: ComObjectHandle, event_class: type
    ) -> ComEventSinkHandle:
        return cast(
            ComEventSinkHandle,
            self.invoke(lambda: self._attach_events(handle, event_class)),
        )

    def get_event_attribute(self, handle: ComEventSinkHandle, name: str) -> object:
        return self.invoke(lambda: self._get_event_attribute(handle, name))

    def set_event_attribute(
        self, handle: ComEventSinkHandle, name: str, value: object
    ) -> None:
        self.invoke(lambda: setattr(self._resolve_event_sink(handle), name, value))

    def close_event_sink(self, handle: ComEventSinkHandle) -> None:
        self.invoke(lambda: self._close_event_sink(handle))

    def abandon_event_sink(self, handle: ComEventSinkHandle) -> None:
        self.invoke(lambda: self._abandon_event_sink(handle))

    def iterate(self, handle: ComObjectHandle) -> ComIteratorHandle:
        return cast(ComIteratorHandle, self.invoke(lambda: self._new_iterator(handle)))

    def snapshot_items(self, handle: ComObjectHandle) -> tuple[object, ...]:
        """Materialize a collection on the STA before a caller mutates it."""
        return cast(
            tuple[object, ...],
            self.invoke(lambda collection: tuple(collection), handle),
        )

    def next_item(self, handle: ComIteratorHandle) -> object:
        return self.invoke(lambda: self._next_iterator(handle))

    def close_iterator(self, handle: ComIteratorHandle) -> None:
        self.invoke(lambda: self._close_iterator(handle))

    def close(self, *, abandon_event_sinks: bool = False) -> None:
        """Stop the worker, unregister its message filter, and uninitialize COM."""
        with self._state_lock:
            self._abandon_event_sinks_on_shutdown |= abandon_event_sinks
            if not self._closing:
                self._closing = True
                self._queue.put(None)
        if get_ident() != self._worker_id:
            self._thread.join()
            error = self._worker_error or self._shutdown_error
            if error is not None:
                raise RuntimeError(
                    "The COM session did not shut down cleanly"
                ) from error

    def _raise_if_unavailable(self) -> None:
        if self._startup_error is not None:
            raise self._startup_error
        if self._worker_error is not None:
            raise RuntimeError("The COM session worker failed") from self._worker_error
        if self._closing or self._closed:
            raise ComSessionClosedError("The COM session is closed")

    def _run(self) -> None:
        message_filter = None
        com_initialized = False
        try:
            import pythoncom

            pythoncom.CoInitialize()
            com_initialized = True
            from py_canoe.core.message_filter import COMRetryMessageFilter

            message_filter = COMRetryMessageFilter()
            message_filter.register()
            with self._state_lock:
                self._worker_id = get_ident()
            self._ready.set()

            while True:
                try:
                    item = self._queue.get(timeout=0.01)
                except Empty:
                    pythoncom.PumpWaitingMessages()
                    continue
                if item is None:
                    break
                if item.future.set_running_or_notify_cancel():
                    try:
                        result = self._execute(item.callback, item.args, item.kwargs)
                    except BaseException as error:  # noqa: BLE001 - always settle the caller's Future.
                        item.future.set_exception(error)
                    else:
                        item.future.set_result(result)
                pythoncom.PumpWaitingMessages()
        except BaseException as error:  # noqa: BLE001 - prevent startup/worker failure from stranding callers.
            with self._state_lock:
                if not self._ready.is_set():
                    self._startup_error = error
                else:
                    self._worker_error = error
        finally:
            try:
                if self._abandon_event_sinks_on_shutdown:
                    self._abandon_all_event_sinks()
                else:
                    self._close_all_event_sinks()
            except Exception as error:  # noqa: BLE001 - finish shutdown after sink cleanup errors.
                if self._shutdown_error is None:
                    self._shutdown_error = error
            self._iterators.clear()
            self._event_sinks.clear()
            self._objects.clear()
            if message_filter is not None:
                try:
                    message_filter.unregister()
                except OSError as error:
                    self._shutdown_error = error
            if com_initialized:
                try:
                    pythoncom.CoUninitialize()
                except pythoncom.com_error as error:
                    if self._shutdown_error is None:
                        self._shutdown_error = error
            with self._state_lock:
                self._closed = True
            self._ready.set()
            failure = self._worker_error or self._shutdown_error
            if failure is None:
                failure = ComSessionClosedError("The COM session worker stopped")
            self._fail_pending(failure)

    def _execute(
        self,
        callback: Callable[..., object],
        args: tuple[object, ...],
        kwargs: dict[str, object],
    ) -> object:
        resolved_args = tuple(self._resolve_handles(arg) for arg in args)
        resolved_kwargs = {
            key: self._resolve_handles(value) for key, value in kwargs.items()
        }
        result = callback(*resolved_args, **resolved_kwargs)
        return self._register_results(result)

    def _resolve_handles(self, value: object) -> object:
        if isinstance(value, ComObjectHandle):
            return self._resolve_handle(value)
        if isinstance(value, ComObjectProxy):
            if value._session is not self:
                raise ValueError("COM references cannot cross session boundaries")
            return self._resolve_handle(value._handle)
        if isinstance(value, tuple):
            return tuple(self._resolve_handles(item) for item in value)
        if isinstance(value, list):
            return [self._resolve_handles(item) for item in value]
        if isinstance(value, dict):
            return {
                self._resolve_handles(key): self._resolve_handles(item)
                for key, item in value.items()
            }
        if self._is_com_object(value):
            raise TypeError(
                "Raw COM objects cannot cross the session boundary; "
                "pass a session-owned ComObjectProxy"
            )
        return value

    def _register_results(self, value: object) -> object:
        if isinstance(value, ComObjectHandle):
            self._resolve_handle(value)
            return value
        if isinstance(value, tuple):
            return tuple(self._register_results(item) for item in value)
        if isinstance(value, list):
            return [self._register_results(item) for item in value]
        if isinstance(value, dict):
            return {
                self._register_results(key): self._register_results(item)
                for key, item in value.items()
            }
        if self._is_com_object(value):
            return self._register_object(value)
        return value

    @staticmethod
    def _is_com_object(value: object) -> bool:
        try:
            object.__getattribute__(value, "_oleobj_")
        except (AttributeError, TypeError):
            return False
        return True

    def _register_object(self, value: object) -> ComObjectHandle:
        import pythoncom

        ole_object = object.__getattribute__(value, "_oleobj_")
        identity = ole_object.QueryInterface(pythoncom.IID_IUnknown)
        # ponytail: PyIUnknown is unhashable, so identity lookup is O(n); use a
        # supported stable pointer key if pywin32 exposes one in the future.
        for object_id, registered in self._objects.items():
            if registered.identity == identity:
                return ComObjectHandle(
                    self._session_id, object_id, self._generation
                )
        object_id = self._next_object_id
        self._next_object_id += 1
        self._objects[object_id] = _RegisteredObject(value, identity)
        return ComObjectHandle(self._session_id, object_id, self._generation)

    def _get_attribute(self, handle: ComObjectHandle, name: str) -> object:
        value = getattr(self._resolve_handle(handle), name)
        if callable(value) and not self._is_com_object(value):
            return ComMethodHandle(
                handle.session_id, handle.object_id, handle.generation, name
            )
        return self._register_results(value)

    def _attach_events(
        self, handle: ComObjectHandle, event_class: type
    ) -> ComEventSinkHandle:
        import win32com.client

        sink = win32com.client.WithEvents(
            self._resolve_handle(handle), event_class
        )
        sink_id = self._next_event_sink_id
        self._next_event_sink_id += 1
        self._event_sinks[sink_id] = sink
        return ComEventSinkHandle(self._session_id, sink_id)

    def _resolve_event_sink(self, handle: ComEventSinkHandle) -> object:
        if handle.session_id != self._session_id:
            raise StaleComReferenceError(
                "The event sink belongs to another COM session"
            )
        try:
            return self._event_sinks[handle.sink_id]
        except KeyError as error:
            raise StaleComReferenceError("The event sink has been released") from error

    def _get_event_attribute(self, handle: ComEventSinkHandle, name: str) -> object:
        value = getattr(self._resolve_event_sink(handle), name)
        if callable(value):
            return _EventMethodHandle(handle, name)
        return self._register_results(value)

    def call_event_method(
        self, handle: ComEventSinkHandle, name: str, args: tuple, kwargs: dict
    ) -> object:
        return self.invoke(
            lambda *resolved_args, **resolved_kwargs: getattr(
                self._resolve_event_sink(handle), name
            )(*resolved_args, **resolved_kwargs),
            *args,
            **kwargs,
        )

    def _close_event_sink(self, handle: ComEventSinkHandle) -> None:
        sink = self._resolve_event_sink(handle)
        del self._event_sinks[handle.sink_id]
        close = getattr(sink, "close", None)
        if callable(close):
            close()

    def _abandon_event_sink(self, handle: ComEventSinkHandle) -> None:
        sink = self._resolve_event_sink(handle)
        del self._event_sinks[handle.sink_id]
        sink_attributes = vars(sink)
        if "_olecp" in sink_attributes:
            # pywin32's generated sink destructor calls close(), which would Unadvise.
            sink_attributes["_olecp"] = None
            if "_olecp_cookie" in sink_attributes:
                sink_attributes["_olecp_cookie"] = None

    def _close_all_event_sinks(self) -> None:
        first_error: Exception | None = None
        for sink_id in tuple(self._event_sinks):
            try:
                self._close_event_sink(
                    ComEventSinkHandle(self._session_id, sink_id)
                )
            except Exception as error:  # noqa: BLE001 - close every sink before reporting failure.
                if first_error is None:
                    first_error = error
        if first_error is not None:
            raise first_error

    def _abandon_all_event_sinks(self) -> None:
        for sink_id in tuple(self._event_sinks):
            self._abandon_event_sink(ComEventSinkHandle(self._session_id, sink_id))

    def _new_iterator(self, handle: ComObjectHandle) -> ComIteratorHandle:
        iterator = iter(self._resolve_handle(handle))
        iterator_id = self._next_iterator_id
        self._next_iterator_id += 1
        self._iterators[iterator_id] = iterator
        return ComIteratorHandle(self._session_id, iterator_id, self._generation)

    def _next_iterator(self, handle: ComIteratorHandle) -> object:
        iterator = self._resolve_iterator(handle)
        try:
            return next(iterator)
        except StopIteration:
            self._close_iterator(handle)
            return _ITERATION_END

    def _resolve_iterator(self, handle: ComIteratorHandle) -> Iterator[object]:
        if (
            handle.session_id != self._session_id
            or handle.generation != self._generation
        ):
            raise StaleComReferenceError(
                "The collection iterator belongs to a stale generation"
            )
        try:
            return self._iterators[handle.iterator_id]
        except KeyError as error:
            raise StaleComReferenceError(
                "The collection iterator has been closed"
            ) from error

    def _close_iterator(self, handle: ComIteratorHandle) -> None:
        if handle.session_id == self._session_id:
            self._iterators.pop(handle.iterator_id, None)

    def _resolve_handle(self, handle: ComObjectHandle) -> object:
        if (
            handle.session_id != self._session_id
            or handle.generation != self._generation
        ):
            raise StaleComReferenceError(
                "The COM reference belongs to a stale session generation"
            )
        registered = self._objects.get(handle.object_id)
        if registered is None:
            raise StaleComReferenceError("The COM reference has been released")
        return registered.value

    def _release_object(self, handle: ComObjectHandle) -> None:
        self._resolve_handle(handle)
        self._objects.pop(handle.object_id)

    def _invalidate_objects(
        self, preserve: tuple[ComObjectHandle, ...] = ()
    ) -> tuple[ComObjectHandle, ...]:
        preserved_objects = tuple(self._resolve_handle(handle) for handle in preserve)
        self._iterators.clear()
        self._objects.clear()
        self._generation += 1
        return tuple(self._register_object(value) for value in preserved_objects)

    def _fail_pending(self, error: BaseException) -> None:
        while True:
            try:
                item = self._queue.get_nowait()
            except Empty:
                return
            if item is not None and not item.future.done():
                item.future.set_exception(error)


class StaleComReferenceError(RuntimeError):
    """Raised when a COM handle is released or belongs to an old generation."""


class ComObjectProxy:
    """Thread-safe facade over a registry-owned COM object."""

    __slots__ = ("_handle", "_session")

    def __init__(self, session: ComSession, handle: ComObjectHandle):
        object.__setattr__(self, "_session", session)
        object.__setattr__(self, "_handle", handle)

    def __getattr__(self, name: str) -> object:
        if name == "_oleobj_":
            raise AttributeError(name)
        return _wrap_result(
            self._session, self._session.get_attribute(self._handle, name)
        )

    def __setattr__(self, name: str, value: object) -> None:
        if name in self.__slots__:
            object.__setattr__(self, name, value)
            return
        self._session.set_attribute(self._handle, name, value)

    def __call__(self, *args: object, **kwargs: object) -> object:
        return _wrap_result(
            self._session, self._session.call_object(self._handle, args, kwargs)
        )

    def __iter__(self) -> Iterator[object]:
        iterator = self._session.iterate(self._handle)
        try:
            while True:
                value = self._session.next_item(iterator)
                if value is _ITERATION_END:
                    return
                yield _wrap_result(self._session, value)
        finally:
            self._session.close_iterator(iterator)

    def snapshot_items(self) -> tuple[object, ...]:
        """Return a stable tuple for iteration that may modify the collection."""
        return tuple(
            _wrap_result(self._session, item)
            for item in self._session.snapshot_items(self._handle)
        )

    def __bool__(self) -> bool:
        return bool(self._session.invoke(lambda obj: bool(obj), self._handle))

    def __len__(self) -> int:
        return int(self._session.invoke(lambda obj: len(obj), self._handle))

    def __getitem__(self, key: object) -> object:
        return _wrap_result(
            self._session,
            self._session.invoke(lambda obj, item: obj[item], self._handle, key),
        )

    def __repr__(self) -> str:
        return f"ComObjectProxy(handle={self._handle!r})"


def invoke_com_dispatch(
    value: ComObjectProxy,
    dispid: int,
    kind: Literal["method", "property_get", "property_put"],
    return_type: tuple[int, int],
    argument_types: tuple[tuple[int, int], ...],
    *arguments: object,
) -> object:
    """Invoke members omitted from CANoe's generated interface on the owning STA."""
    invocation_kind = {"method": 1, "property_get": 2, "property_put": 4}[kind]
    return value._session.invoke(
        _invoke_dispatch_types,
        value,
        dispid,
        invocation_kind,
        return_type,
        argument_types,
        arguments,
    )


def _invoke_dispatch_types(
    com_object: object,
    dispid: int,
    invocation_kind: int,
    return_type: tuple[int, int],
    argument_types: tuple[tuple[int, int], ...],
    arguments: tuple[object, ...],
) -> object:
    return com_object._oleobj_.InvokeTypes(
        dispid,
        0,
        invocation_kind,
        return_type,
        argument_types,
        *arguments,
    )


class _ComMethodProxy:
    __slots__ = ("_handle", "_session")

    def __init__(self, session: ComSession, handle: ComMethodHandle):
        self._session = session
        self._handle = handle

    def __call__(self, *args: object, **kwargs: object) -> object:
        return _wrap_result(
            self._session,
            self._session.call_method(self._handle, args, kwargs),
        )


class ComEventSinkProxy:
    """Safe access to event state while keeping the pywin32 sink on the STA."""

    __slots__ = ("_handle", "_session")

    def __init__(self, session: ComSession, handle: ComEventSinkHandle):
        object.__setattr__(self, "_session", session)
        object.__setattr__(self, "_handle", handle)

    def __getattr__(self, name: str) -> object:
        if name == "_oleobj_":
            raise AttributeError(name)
        return _wrap_result(
            self._session,
            self._session.get_event_attribute(self._handle, name),
        )

    def __setattr__(self, name: str, value: object) -> None:
        if name in self.__slots__:
            object.__setattr__(self, name, value)
            return
        self._session.set_event_attribute(self._handle, name, value)

    def close(self) -> None:
        self._session.close_event_sink(self._handle)

    def abandon(self) -> None:
        self._session.abandon_event_sink(self._handle)


class _ComEventMethodProxy:
    __slots__ = ("_handle", "_session")

    def __init__(self, session: ComSession, handle: _EventMethodHandle):
        self._session = session
        self._handle = handle

    def __call__(self, *args: object, **kwargs: object) -> object:
        return _wrap_result(
            self._session,
            self._session.call_event_method(
                self._handle.event_sink, self._handle.name, args, kwargs
            ),
        )


def _wrap_result(session: ComSession, value: object) -> object:
    if isinstance(value, ComObjectHandle):
        return ComObjectProxy(session, value)
    if isinstance(value, ComMethodHandle):
        return _ComMethodProxy(session, value)
    if isinstance(value, ComEventSinkHandle):
        return ComEventSinkProxy(session, value)
    if isinstance(value, _EventMethodHandle):
        return _ComEventMethodProxy(session, value)
    if isinstance(value, list):
        return [_wrap_result(session, item) for item in value]
    if isinstance(value, tuple):
        return tuple(_wrap_result(session, item) for item in value)
    if isinstance(value, dict):
        return {
            _wrap_result(session, key): _wrap_result(session, item)
            for key, item in value.items()
        }
    return value


def dispatch_com_object(value: object) -> object:
    """Keep session proxies and test doubles, but reject raw pywin32 COM references."""
    if isinstance(value, ComObjectProxy):
        return value
    if ComSession._is_com_object(value):
        raise TypeError("Raw COM objects must be owned by a ComSession")
    return value


def with_com_events(value: object, event_class: type) -> object:
    """Attach events on the owning STA when passed a registry proxy."""
    if isinstance(value, ComObjectProxy):
        handle = value._session.attach_events(value._handle, event_class)
        return ComEventSinkProxy(value._session, handle)
    if ComSession._is_com_object(value):
        raise TypeError("Raw COM event sources must be owned by a ComSession")
    import win32com.client

    return win32com.client.WithEvents(value, event_class)
