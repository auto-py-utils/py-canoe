import pytest
from unittest.mock import MagicMock, PropertyMock, patch

from py_canoe.exceptions import ConfigurationNotLoadedError
from py_canoe.core.child_elements.simulation_setup import SimulationSetup
from py_canoe.core.child_elements.buses import Buses
from py_canoe.core.child_elements.bus import Bus
from py_canoe.core.child_elements.databases import Databases
from py_canoe.core.child_elements.database import Database


@pytest.fixture(autouse=True)
def _patch_child_element_dispatch():
    with patch("py_canoe.core.child_elements.bus.win32com.client.Dispatch", side_effect=lambda x: x), \
         patch("py_canoe.core.child_elements.simulation_setup.win32com.client.Dispatch", side_effect=lambda x: x), \
         patch("py_canoe.core.child_elements.database.win32com.client.Dispatch", side_effect=lambda x: x):
        yield


def _make_sim_buses(bus_specs):
    buses_com = MagicMock()
    buses_com.Count = len(bus_specs)

    def buses_item(index):
        spec = bus_specs[index - 1]
        bus_com = MagicMock()
        bus_com.Name = spec["name"]
        dbs_com = MagicMock()
        dbs_com.Count = len(spec["dbs"])

        def dbs_item(j):
            db_spec = spec["dbs"][j - 1]
            db_com = MagicMock()
            db_com.FullName = db_spec["full_name"]
            db_com.Name = db_spec["name"]
            return db_com

        dbs_com.Item.side_effect = dbs_item
        bus_com.Databases = dbs_com
        return bus_com

    buses_com.Item.side_effect = buses_item

    sim_buses = Buses.__new__(Buses)
    sim_buses.com_object = buses_com
    return sim_buses


def _make_bus_obj(bus_specs):
    """Returns a Bus-like object whose app.configuration.simulation_setup.buses uses bus_specs."""
    from py_canoe.core.bus import Bus

    sim_buses = _make_sim_buses(bus_specs)

    sim_setup = MagicMock(spec=SimulationSetup)
    type(sim_setup).buses = PropertyMock(return_value=sim_buses)

    app = MagicMock()
    app.configuration.simulation_setup = sim_setup

    bus_obj = Bus.__new__(Bus)
    bus_obj.app = app
    return bus_obj


class TestSimulationSetupClasses:
    def test_simulation_setup_buses_property(self):
        com = MagicMock()
        buses_com = MagicMock()
        com.Buses = buses_com
        ss = SimulationSetup(com)
        result = ss.buses
        assert isinstance(result, Buses)

    def test_simulation_buses_count(self):
        com = MagicMock()
        com.Count = 3
        sb = Buses(com)
        assert sb.count == 3

    def test_simulation_buses_item_returns_simulation_bus(self):
        inner_com = MagicMock()
        buses_com = MagicMock()
        buses_com.Item.return_value = inner_com
        buses_com.Count = 1
        sb = Buses(buses_com)
        result = sb.item(1)
        assert isinstance(result, Bus)

    def test_simulation_bus_name(self):
        com = MagicMock()
        com.Name = "CAN1"
        bus = Bus(com)
        assert bus.name == "CAN1"

    def test_simulation_bus_databases_property(self):
        dbs_com = MagicMock()
        com = MagicMock()
        com.Databases = dbs_com
        bus = Bus(com)
        result = bus.databases
        assert isinstance(result, Databases)

    def test_simulation_bus_databases_count(self):
        com = MagicMock()
        com.Count = 2
        dbs = Databases(com)
        assert dbs.count == 2

    def test_simulation_bus_database_properties(self):
        com = MagicMock()
        com.FullName = "C:/path/to/db.dbc"
        com.Name = "db"
        db = Database(com)
        assert db.full_name == "C:/path/to/db.dbc"
        assert db.name == "db"


class TestGetSimulationBusNames:
    def test_returns_all_names(self):
        bus_specs = [
            {"name": "CAN", "dbs": []},
            {"name": "LIN", "dbs": []},
        ]
        bus_obj = _make_bus_obj(bus_specs)
        result = bus_obj.get_simulation_bus_names()
        assert result == ["CAN", "LIN"]

    def test_includes_buses_with_empty_name(self):
        bus_specs = [
            {"name": "CAN", "dbs": []},
            {"name": "", "dbs": []},
            {"name": "ETH", "dbs": []},
        ]
        bus_obj = _make_bus_obj(bus_specs)
        result = bus_obj.get_simulation_bus_names()
        assert result == ["CAN", "", "ETH"]

    def test_skips_buses_with_none_name(self):
        from py_canoe.core.bus import Bus

        buses_com = MagicMock()
        buses_com.Count = 2

        def buses_item(index):
            bus_com = MagicMock()
            bus_com.Name = None if index == 1 else "CAN"
            bus_com.Databases.Count = 0
            return bus_com

        buses_com.Item.side_effect = buses_item
        sim_buses = Buses.__new__(Buses)
        sim_buses.com_object = buses_com

        sim_setup = MagicMock(spec=SimulationSetup)
        type(sim_setup).buses = PropertyMock(return_value=sim_buses)

        app = MagicMock()
        app.configuration.simulation_setup = sim_setup

        bus_obj = Bus.__new__(Bus)
        bus_obj.app = app
        result = bus_obj.get_simulation_bus_names()
        assert result == ["CAN"]

    def test_returns_empty_list_when_no_buses(self):
        bus_obj = _make_bus_obj([])
        result = bus_obj.get_simulation_bus_names()
        assert result == []

    def test_raises_on_exception(self):
        from py_canoe.core.bus import Bus

        app = MagicMock()
        type(app.configuration.simulation_setup).buses = PropertyMock(side_effect=Exception("COM error"))
        bus_obj = Bus.__new__(Bus)
        bus_obj.app = app
        with pytest.raises(ConfigurationNotLoadedError):
            bus_obj.get_simulation_bus_names()


class TestGetSimulationDatabasePaths:
    def test_returns_all_paths(self):
        bus_specs = [
            {"name": "CAN", "dbs": [
                {"full_name": "C:/dbs/can.dbc", "name": "can"},
                {"full_name": "C:/dbs/other.dbc", "name": "other"},
            ]},
            {"name": "LIN", "dbs": [
                {"full_name": "C:/dbs/lin.ldf", "name": "lin"},
            ]},
        ]
        bus_obj = _make_bus_obj(bus_specs)
        result = bus_obj.get_simulation_database_paths()
        assert "C:/dbs/can.dbc" in result
        assert "C:/dbs/other.dbc" in result
        assert "C:/dbs/lin.ldf" in result
        assert len(result) == 3

    def test_includes_empty_full_name(self):
        bus_specs = [
            {"name": "CAN", "dbs": [
                {"full_name": "C:/dbs/can.dbc", "name": "can"},
                {"full_name": "", "name": "empty"},
            ]},
        ]
        bus_obj = _make_bus_obj(bus_specs)
        result = bus_obj.get_simulation_database_paths()
        assert result == ["C:/dbs/can.dbc", ""]

    def test_skips_none_full_name(self):
        from py_canoe.core.bus import Bus

        buses_com = MagicMock()
        buses_com.Count = 1

        def buses_item(index):
            bus_com = MagicMock()
            bus_com.Name = "CAN"
            dbs_com = MagicMock()
            dbs_com.Count = 2

            def dbs_item(j):
                db_com = MagicMock()
                db_com.FullName = None if j == 1 else "C:/dbs/can.dbc"
                db_com.Name = "db"
                return db_com

            dbs_com.Item.side_effect = dbs_item
            bus_com.Databases = dbs_com
            return bus_com

        buses_com.Item.side_effect = buses_item
        sim_buses = Buses.__new__(Buses)
        sim_buses.com_object = buses_com

        sim_setup = MagicMock(spec=SimulationSetup)
        type(sim_setup).buses = PropertyMock(return_value=sim_buses)

        app = MagicMock()
        app.configuration.simulation_setup = sim_setup

        bus_obj = Bus.__new__(Bus)
        bus_obj.app = app
        result = bus_obj.get_simulation_database_paths()
        assert result == ["C:/dbs/can.dbc"]

    def test_returns_empty_list_when_no_databases(self):
        bus_specs = [
            {"name": "CAN", "dbs": []},
            {"name": "LIN", "dbs": []},
        ]
        bus_obj = _make_bus_obj(bus_specs)
        result = bus_obj.get_simulation_database_paths()
        assert result == []

    def test_raises_on_exception(self):
        from py_canoe.core.bus import Bus

        app = MagicMock()
        type(app.configuration.simulation_setup).buses = PropertyMock(side_effect=Exception("COM error"))
        bus_obj = Bus.__new__(Bus)
        bus_obj.app = app
        with pytest.raises(ConfigurationNotLoadedError):
            bus_obj.get_simulation_database_paths()
