import sys
from threading import get_ident
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

import pytest

from py_canoe.core.application import Application
from py_canoe.core.child_elements.channels import Channels
from py_canoe.core.child_elements.variable import Variable
from py_canoe.core.com_session import (
    ComObjectHandle,
    ComObjectProxy,
    ComSession,
    ComSessionClosedError,
    StaleComReferenceError,
    dispatch_com_object,
    with_com_events,
)
from py_canoe.core.configuration import Configuration


class _FakeIUnknown:
    def __init__(self, pointer: int):
        self.pointer = pointer

    def __int__(self) -> int:
        return self.pointer

    def __eq__(self, other):
        return isinstance(other, _FakeIUnknown) and self.pointer == other.pointer


class _FakeOleObject:
    def __init__(self, pointer: int):
        self.pointer = pointer

    def QueryInterface(self, interface_id):
        return _FakeIUnknown(self.pointer)


class _FakeComObject:
    def __init__(self, pointer: int, name: str, children=None):
        self._oleobj_ = _FakeOleObject(pointer)
        self.name = name
        self.children = children or []

    def rename(self, name: str):
        self.name = name
        return self.name

    def __iter__(self):
        return iter(self.children)


class _FakeApplication(_FakeComObject):
    def __init__(self):
        super().__init__(77, "CANoe")
        self.Name = "CANoe"
        self.Configuration = _FakeComObject(78, "configuration")
        self.Configuration.FullName = ""


class _FakeCollection(_FakeComObject):
    def __init__(self):
        super().__init__(4567, "collection", children=[_FakeComObject(4568, "one")])
        self.item_calls = []

    @property
    def Count(self):
        return len(self.children)

    def Item(self, index):
        self.item_calls.append(index)
        return self.children[index - 1]


class _FakeEventSink:
    def __init__(self):
        self.STARTED = False
        self.closed = False
        self._olecp = object()
        self._olecp_cookie = 1

    def close(self):
        self.closed = True


@pytest.fixture
def com_session():
    session = ComSession()
    try:
        yield session
    finally:
        session.close()


@pytest.mark.unit
def test_com_session_runs_and_reenters_on_its_sta_thread(com_session):
    owner_thread = com_session.invoke(get_ident)
    nested_thread = com_session.invoke(lambda: com_session.invoke(get_ident))

    assert owner_thread != get_ident()
    assert nested_thread == owner_thread


@pytest.mark.unit
def test_com_session_propagates_callback_errors_and_remains_usable(com_session):
    def fail():
        raise ValueError("callback failed")

    with pytest.raises(ValueError, match="callback failed"):
        com_session.invoke(fail)
    assert com_session.invoke(lambda: 42) == 42


@pytest.mark.unit
def test_com_session_rejects_work_after_close():
    session = ComSession()
    session.close()

    with pytest.raises(ComSessionClosedError):
        session.invoke(lambda: None)


@pytest.mark.unit
def test_dispatch_helper_rejects_raw_com_objects():
    raw_com_object = _FakeComObject(1234, "raw")

    with pytest.raises(TypeError, match="must be owned by a ComSession"):
        dispatch_com_object(raw_com_object)
    with pytest.raises(TypeError, match="event sources must be owned"):
        with_com_events(raw_com_object, object)


@pytest.mark.unit
def test_com_session_rejects_raw_com_arguments(com_session):
    raw_com_object = _FakeComObject(1235, "raw")

    with pytest.raises(TypeError, match="cannot cross the session boundary"):
        com_session.invoke(lambda value: value.name, raw_com_object)


@pytest.mark.unit
def test_variable_full_name_falls_back_to_its_namespace(com_session):
    def create_variable():
        variable = _FakeComObject(1236, "speed")
        variable.Name = "speed"
        return variable

    handle = com_session.invoke(create_variable)
    variable = Variable(
        ComObjectProxy(com_session, handle),
        namespace_name="demo::engine",
    )

    assert variable.full_name == "demo::engine::speed"


@pytest.mark.unit
def test_registry_deduplicates_com_identity_and_invalidates_old_handles(com_session):
    first = com_session.invoke(lambda: _FakeComObject(1234, "first"))
    second = com_session.invoke(lambda: _FakeComObject(1234, "second"))

    assert isinstance(first, ComObjectHandle)
    assert first == second
    assert com_session.invoke(lambda obj: obj.name, first) == "first"

    com_session.invalidate()
    with pytest.raises(StaleComReferenceError):
        com_session.invoke(lambda obj: obj.name, first)


@pytest.mark.unit
def test_registry_release_invalidates_the_released_handle(com_session):
    handle = com_session.invoke(lambda: _FakeComObject(5678, "released"))

    com_session.release(handle)

    with pytest.raises(StaleComReferenceError):
        com_session.invoke(lambda obj: obj.name, handle)


@pytest.mark.unit
def test_com_proxy_routes_properties_methods_and_iteration_through_the_sta(com_session):
    handle = com_session.invoke(
        lambda: _FakeComObject(9012, "root", children=[_FakeComObject(9013, "child")])
    )
    proxy = ComObjectProxy(com_session, handle)

    assert proxy.name == "root"
    assert proxy.rename("updated") == "updated"
    proxy.name = "renamed"
    assert proxy.name == "renamed"
    assert [child.name for child in proxy] == ["child"]
    iterator = iter(proxy)
    next(iterator)
    assert com_session.invoke(lambda: len(com_session._iterators)) == 1
    iterator.close()
    assert com_session.invoke(lambda: len(com_session._iterators)) == 0


@pytest.mark.unit
def test_collection_wrapper_iteration_fetches_items_on_demand(com_session):
    handle = com_session.invoke(_FakeCollection)
    collection = ComObjectProxy(com_session, handle)
    items = Channels(collection).iter_items()

    assert com_session.invoke(lambda value: value.item_calls, handle) == []
    next(items)
    assert com_session.invoke(lambda value: value.item_calls, handle) == [1]
    snapshot = collection.snapshot_items()
    com_session.invoke(lambda value: value.children.clear(), handle)
    assert [item.name for item in snapshot] == ["one"]


@pytest.mark.unit
def test_configuration_defers_collection_loading_until_requested():
    with patch(
        "py_canoe.core.configuration.dispatch_com_object",
        side_effect=lambda value: value,
    ):
        configuration = Configuration(
            SimpleNamespace(com_object=SimpleNamespace(Configuration=object()))
        )
    load_calls = []
    configuration.configuration_test_setup = lambda: SimpleNamespace(
        test_environments=SimpleNamespace(
            fetch_all_test_environments=lambda: load_calls.append(True) or {}
        )
    )

    assert load_calls == []
    assert configuration._test_setup_environments == {}
    assert configuration._test_setup_environments == {}
    assert load_calls == [True]


@pytest.mark.unit
def test_application_creates_its_root_com_object_on_the_sta():
    app = Application(enable_events=False)
    creation_threads = []

    def create_application(prog_id):
        creation_threads.append(get_ident())
        return _FakeApplication()

    try:
        with patch(
            "py_canoe.core.application.gencache.EnsureDispatch",
            side_effect=create_application,
        ):
            app._launch_application()
        assert isinstance(app.com_object, ComObjectProxy)
        assert app.name == "CANoe"
        assert creation_threads == [app._com_session.invoke(get_ident)]
    finally:
        app.close()


@pytest.mark.unit
def test_gencache_fallback_preserves_generated_package_for_event_support():
    app = Application(enable_events=False)
    gen_py_package = ModuleType("win32com.gen_py")
    corrupt_typelib = ModuleType("win32com.gen_py.corrupt_typelib")

    try:
        with patch.dict(
            sys.modules,
            {
                "win32com.gen_py": gen_py_package,
                "win32com.gen_py.corrupt_typelib": corrupt_typelib,
            },
        ):
            with (
                patch(
                    "py_canoe.core.application.gencache.EnsureDispatch",
                    side_effect=AttributeError("broken cache"),
                ),
                patch(
                    "py_canoe.core.application.win32com.client.Dispatch",
                    return_value=_FakeApplication(),
                ),
            ):
                app._launch_application()

            assert sys.modules["win32com.gen_py"] is gen_py_package
            assert "win32com.gen_py.corrupt_typelib" not in sys.modules
    finally:
        app.close()


@pytest.mark.unit
def test_event_sink_state_and_release_are_routed_to_the_sta(com_session):
    com_handle = com_session.invoke(lambda: _FakeComObject(3456, "measurement"))
    com_proxy = ComObjectProxy(com_session, com_handle)
    event_sink = _FakeEventSink()

    with patch("win32com.client.WithEvents", return_value=event_sink):
        events = with_com_events(com_proxy, object)
        events.STARTED = True
        assert events.STARTED is True
        events.close()

    assert event_sink.closed is True


@pytest.mark.unit
def test_event_sink_can_be_abandoned_without_unadvising(com_session):
    app = Application()
    app._com_session = com_session
    com_handle = com_session.invoke(lambda: _FakeComObject(3457, "measurement"))
    com_proxy = ComObjectProxy(com_session, com_handle)
    event_sink = _FakeEventSink()

    with patch("win32com.client.WithEvents", return_value=event_sink):
        app.application_events = with_com_events(com_proxy, object)
        app.close(abandon_event_sinks=True)

    assert event_sink.closed is False
    assert event_sink._olecp is None
    assert event_sink._olecp_cookie is None
    assert not com_session._event_sinks
