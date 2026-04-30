import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from py_canoe.core.child_elements.namespaces import Namespaces
from py_canoe.core.child_elements.variables import Variables
from py_canoe.core.system import System
from py_canoe.exceptions import PyCanoeError, NamespaceNotFoundError


def _make_namespaces(names):
    com = MagicMock()
    com.Count = len(names)

    def item_side_effect(index):
        ns = MagicMock()
        ns.Name = names[index - 1]
        return ns

    com.Item.side_effect = item_side_effect
    ns_obj = Namespaces.__new__(Namespaces)
    ns_obj.com_object = com
    return ns_obj


def _make_variables(entries):
    com = MagicMock()
    com.Count = len(entries)

    def item_side_effect(index):
        e = entries[index - 1]
        var_com = MagicMock()
        var_com.Name = e["name"]
        var_com.Value = e["value"]
        var_com.FullName = e["full_name"]
        return var_com

    com.Item.side_effect = item_side_effect
    var_obj = Variables.__new__(Variables)
    var_obj.com_object = com
    return var_obj


class TestNamespacesFetchAll:
    def test_returns_all_namespaces(self):
        ns_obj = _make_namespaces(["demo", "TestControl"])
        result = ns_obj.fetch_all()
        assert len(result) == 2
        assert result[0].name == "demo"
        assert result[1].name == "TestControl"

    def test_returns_empty_list_when_none(self):
        ns_obj = _make_namespaces([])
        result = ns_obj.fetch_all()
        assert result == []

    def test_raises_on_exception_mid_iteration(self):
        com = MagicMock()
        com.Count = 3
        call_count = [0]

        def item_side_effect(index):
            call_count[0] += 1
            if call_count[0] == 2:
                raise Exception("COM error on item 2")
            ns = MagicMock()
            ns.Name = f"ns_{index}"
            return ns

        com.Item.side_effect = item_side_effect
        ns_obj = Namespaces.__new__(Namespaces)
        ns_obj.com_object = com
        with pytest.raises(Exception):
            ns_obj.fetch_all()

    def test_raises_on_count_exception(self):
        com = MagicMock()
        type(com).Count = PropertyMock(side_effect=Exception("COM error"))
        ns_obj = Namespaces.__new__(Namespaces)
        ns_obj.com_object = com
        with pytest.raises(Exception):
            ns_obj.fetch_all()


class TestVariablesFetchAll:
    def test_returns_all_variables(self):
        entries = [
            {"name": "speed", "value": 100, "full_name": "demo::speed"},
            {"name": "level", "value": 5,   "full_name": "demo::level"},
        ]
        var_obj = _make_variables(entries)
        with patch("py_canoe.core.child_elements.variable.win32com.client.Dispatch", side_effect=lambda x: x):
            result = var_obj.fetch_all()
        assert len(result) == 2
        assert result[0].name == "speed"
        assert result[1].name == "level"

    def test_returns_empty_list_when_none(self):
        var_obj = _make_variables([])
        result = var_obj.fetch_all()
        assert result == []

    def test_raises_on_count_exception(self):
        com = MagicMock()
        type(com).Count = PropertyMock(side_effect=Exception("COM error"))
        var_obj = Variables.__new__(Variables)
        var_obj.com_object = com
        with pytest.raises(Exception):
            var_obj.fetch_all()


class TestSystemGetAllNamespaceNames:
    def _make_system(self, names):
        app = MagicMock()
        com = MagicMock()
        com.Count = len(names)

        def item_side_effect(index):
            ns = MagicMock()
            ns.Name = names[index - 1]
            return ns

        com.Item.side_effect = item_side_effect
        app.com_object.System.Namespaces = com
        sys_obj = System.__new__(System)
        sys_obj.com_object = app.com_object.System
        return sys_obj

    def test_returns_names(self):
        sys_obj = self._make_system(["demo", "TestControl"])
        result = sys_obj.get_all_namespace_names()
        assert "demo" in result
        assert "TestControl" in result

    def test_raises_on_exception(self):
        sys_obj = System.__new__(System)
        com = MagicMock()
        type(com).Namespaces = PropertyMock(side_effect=Exception("COM error"))
        sys_obj.com_object = com
        with pytest.raises(PyCanoeError):
            sys_obj.get_all_namespace_names()


class TestSystemGetAllVariablesInNamespace:
    def _make_system_with_namespace(self, var_entries):
        sys_obj = System.__new__(System)
        com = MagicMock()
        ns_com = MagicMock()
        vars_com = MagicMock()
        vars_com.Count = len(var_entries)

        def item_side_effect(index):
            e = var_entries[index - 1]
            var_com = MagicMock()
            var_com.Name = e["name"]
            var_com.Value = e["value"]
            var_com.FullName = e["full_name"]
            return var_com

        vars_com.Item.side_effect = item_side_effect
        ns_com.Variables = vars_com
        com.Namespaces.return_value = ns_com
        sys_obj.com_object = com
        return sys_obj

    def test_returns_correct_dict_keys(self):
        entries = [{"name": "speed", "value": 10, "full_name": "demo::speed"}]
        sys_obj = self._make_system_with_namespace(entries)
        with patch("py_canoe.core.child_elements.variable.win32com.client.Dispatch", side_effect=lambda x: x):
            result = sys_obj.get_all_variables_in_namespace("demo")
        assert len(result) == 1
        assert result[0]["name"] == "speed"
        assert result[0]["value"] == 10
        assert result[0]["full_name"] == "demo::speed"

    def test_raises_for_unknown_namespace(self):
        sys_obj = System.__new__(System)
        com = MagicMock()
        com.Namespaces.side_effect = Exception("namespace not found")
        sys_obj.com_object = com
        with pytest.raises(NamespaceNotFoundError):
            sys_obj.get_all_variables_in_namespace("nonexistent")

    def test_returns_empty_list_when_no_variables(self):
        sys_obj = self._make_system_with_namespace([])
        result = sys_obj.get_all_variables_in_namespace("empty_ns")
        assert result == []

    def test_raises_pycanoe_error_on_fetch_failure(self):
        sys_obj = System.__new__(System)
        com = MagicMock()
        ns_com = MagicMock()
        vars_com = MagicMock()
        type(vars_com).Count = PropertyMock(side_effect=Exception("COM error during fetch"))
        ns_com.Variables = vars_com
        com.Namespaces.return_value = ns_com
        sys_obj.com_object = com
        with pytest.raises(PyCanoeError):
            sys_obj.get_all_variables_in_namespace("demo")
