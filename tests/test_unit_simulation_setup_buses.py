import pytest
from unittest.mock import MagicMock, PropertyMock, patch

from py_canoe.helpers.exceptions import ConfigurationNotLoadedError
from py_canoe.core.child_elements.simulation_setup import SimulationSetup
from py_canoe.core.child_elements.buses import Buses
from py_canoe.core.child_elements.bus import Bus
from py_canoe.core.child_elements.databases import Databases
from py_canoe.core.child_elements.database import Database
from py_canoe.core.configuration import Configuration


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


def _make_canoe_with_sim_buses(bus_specs):
    """Returns a CANoe-like object whose application.configuration.simulation_setup.buses uses bus_specs."""
    from py_canoe.canoe import CANoe

    sim_buses = _make_sim_buses(bus_specs)

    sim_setup = MagicMock(spec=SimulationSetup)
    type(sim_setup).buses = PropertyMock(return_value=sim_buses)

    app = MagicMock()
    app.configuration.simulation_setup = sim_setup

    canoe = CANoe.__new__(CANoe)
    canoe.application = app
    return canoe


class TestSimulationSetupClasses:
    def test_canoe_normalizes_legacy_bus_type_inputs(self):
        from py_canoe.canoe import CANoe
        from py_canoe.helpers.bus_type import BusType

        assert CANoe._normalize_bus_type(BusType.CAN) is BusType.CAN
        assert CANoe._normalize_bus_type("CAN") is BusType.CAN
        assert CANoe._normalize_bus_type("can") is BusType.CAN
        assert CANoe._normalize_bus_type(1) is BusType.CAN

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
        com.Path = "C:/path/to"
        com.Channel = 1
        db = Database(com)
        assert db.full_name == "C:/path/to/db.dbc"
        assert db.name == "db"
        assert db.path == "C:/path/to"
        assert db.channel == 1

    def test_database_channel_setter(self):
        com = MagicMock()
        com.Channel = 1
        db = Database(com)
        db.channel = 2
        assert com.Channel == 2

    def test_database_full_name_setter(self):
        com = MagicMock()
        com.FullName = "old.dbc"
        db = Database(com)
        db.full_name = "new.dbc"
        assert com.FullName == "new.dbc"

    def test_databases_item_returns_list_when_no_index(self):
        com = MagicMock()
        com.Count = 2
        db1, db2 = MagicMock(), MagicMock()
        com.Item.side_effect = [db1, db2]
        dbs = Databases(com)
        result = dbs.item()
        assert len(result) == 2
        assert all(isinstance(r, Database) for r in result)

    def test_databases_add(self):
        com = MagicMock()
        new_db_com = MagicMock()
        com.Add.return_value = new_db_com
        dbs = Databases(com)
        result = dbs.add("C:/path/to/new.dbc")
        com.Add.assert_called_once_with("C:/path/to/new.dbc")
        assert isinstance(result, Database)

    def test_databases_add_network(self):
        com = MagicMock()
        new_db_com = MagicMock()
        com.AddNetwork.return_value = new_db_com
        dbs = Databases(com)
        result = dbs.add_network("my.dbc", "CAN1")
        com.AddNetwork.assert_called_once_with("my.dbc", "CAN1")
        assert isinstance(result, Database)

    def test_databases_remove(self):
        com = MagicMock()
        dbs = Databases(com)
        dbs.remove(1)
        com.Remove.assert_called_once_with(1)

    def test_add_database_handles_bus_without_name_attribute(self):
        class _BusComWithoutName:
            def __init__(self):
                self._channels = MagicMock()
                self._channels.Count = 1
                self._channels.Item.return_value = MagicMock(Number=1)
                self.Channels = self._channels

        cfg = Configuration.__new__(Configuration)
        cfg.app = MagicMock()
        cfg.app.measurement.running = False

        bus_com = _BusComWithoutName()
        buses_com = MagicMock()
        buses_com.Count = 1
        buses_com.Item.return_value = bus_com

        dbs_com = MagicMock()
        db_com = MagicMock()
        db_com.Channel = 0
        dbs_com.Add.return_value = db_com

        sim_setup_com = MagicMock()
        sim_setup_com.Buses = buses_com

        cfg.com_object = MagicMock()
        cfg.com_object.SimulationSetup = sim_setup_com
        cfg.com_object.GeneralSetup.DatabaseSetup.Databases = dbs_com

        result = cfg.add_database("C:/path/to/db.dbc", 1)

        assert result is True
        dbs_com.Add.assert_called_once_with("C:/path/to/db.dbc")
        assert db_com.Channel == 1

    def test_add_database_falls_back_to_configuration_database_collection(self):
        class _BusComWithoutChannelsAndDatabases:
            pass

        cfg = Configuration.__new__(Configuration)
        cfg.app = MagicMock()
        cfg.app.measurement.running = False

        bus_com = _BusComWithoutChannelsAndDatabases()
        buses_com = MagicMock()
        buses_com.Count = 1
        buses_com.Item.return_value = bus_com

        dbs_com = MagicMock()
        db_com = MagicMock()
        db_com.Channel = 0
        dbs_com.Add.return_value = db_com

        sim_setup_com = MagicMock()
        sim_setup_com.Buses = buses_com

        cfg.com_object = MagicMock()
        cfg.com_object.SimulationSetup = sim_setup_com
        cfg.com_object.GeneralSetup.DatabaseSetup.Databases = dbs_com

        result = cfg.add_database("C:/path/to/db.dbc", 1)

        assert result is True
        dbs_com.Add.assert_called_once_with("C:/path/to/db.dbc")
        assert db_com.Channel == 1


class TestGetSimulationBusNames:
    def test_bus_name_falls_back_to_network_names_when_com_member_is_missing(self):
        from py_canoe.canoe import CANoe

        class _BusComWithoutName:
            def __init__(self):
                self.Count = 0

        buses_com = MagicMock()
        buses_com.Count = 1
        buses_com.Item.return_value = _BusComWithoutName()

        sim_buses = Buses.__new__(Buses)
        sim_buses.com_object = buses_com

        sim_setup = MagicMock(spec=SimulationSetup)
        type(sim_setup).buses = PropertyMock(return_value=sim_buses)

        app = MagicMock()
        app.configuration.simulation_setup = sim_setup
        app.networks.get_all_network_names.return_value = ["CAN1", "CAN2"]

        canoe = CANoe.__new__(CANoe)
        canoe.application = app
        result = canoe.get_simulation_bus_names()

        assert result == ["CAN1", "CAN2"]

    def test_returns_all_names(self):
        bus_specs = [
            {"name": "CAN", "dbs": []},
            {"name": "LIN", "dbs": []},
        ]
        canoe = _make_canoe_with_sim_buses(bus_specs)
        result = canoe.get_simulation_bus_names()
        assert result == ["CAN", "LIN"]

    def test_includes_buses_with_empty_name(self):
        bus_specs = [
            {"name": "CAN", "dbs": []},
            {"name": "", "dbs": []},
            {"name": "ETH", "dbs": []},
        ]
        canoe = _make_canoe_with_sim_buses(bus_specs)
        result = canoe.get_simulation_bus_names()
        assert result == ["CAN", "", "ETH"]

    def test_skips_buses_with_none_name(self):
        from py_canoe.canoe import CANoe

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

        canoe = CANoe.__new__(CANoe)
        canoe.application = app
        result = canoe.get_simulation_bus_names()
        assert result == ["CAN"]

    def test_returns_empty_list_when_no_buses(self):
        canoe = _make_canoe_with_sim_buses([])
        result = canoe.get_simulation_bus_names()
        assert result == []

    def test_raises_on_exception(self):
        from py_canoe.canoe import CANoe

        app = MagicMock()
        type(app.configuration.simulation_setup).buses = PropertyMock(side_effect=Exception("COM error"))
        canoe = CANoe.__new__(CANoe)
        canoe.application = app
        with pytest.raises(ConfigurationNotLoadedError):
            canoe.get_simulation_bus_names()


class TestGetSimulationDatabasePaths:
    def test_returns_paths_from_configuration_database_collection_when_bus_databases_are_missing(self):
        from py_canoe.canoe import CANoe

        class _BusComWithoutDatabases:
            pass

        buses_com = MagicMock()
        buses_com.Count = 1
        buses_com.Item.return_value = _BusComWithoutDatabases()

        sim_buses = Buses.__new__(Buses)
        sim_buses.com_object = buses_com

        sim_setup = MagicMock(spec=SimulationSetup)
        type(sim_setup).buses = PropertyMock(return_value=sim_buses)

        cfg = MagicMock()
        cfg_sim_setup = MagicMock()
        cfg_sim_setup.Buses = buses_com
        cfg.SimulationSetup = cfg_sim_setup

        cfg_dbs_com = MagicMock()
        cfg_dbs_com.Count = 1
        cfg_db_com = MagicMock()
        cfg_db_com.FullName = "C:/dbs/cfg.dbc"
        cfg_dbs_com.Item.return_value = cfg_db_com

        cfg.GeneralSetup.DatabaseSetup.Databases = cfg_dbs_com

        app = MagicMock()
        app.configuration.simulation_setup = sim_setup
        app.configuration.com_object = cfg

        canoe = CANoe.__new__(CANoe)
        canoe.application = app

        result = canoe.get_simulation_database_paths()

        assert result == ["C:/dbs/cfg.dbc"]

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
        canoe = _make_canoe_with_sim_buses(bus_specs)
        result = canoe.get_simulation_database_paths()
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
        canoe = _make_canoe_with_sim_buses(bus_specs)
        result = canoe.get_simulation_database_paths()
        assert result == ["C:/dbs/can.dbc", ""]

    def test_skips_none_full_name(self):
        from py_canoe.canoe import CANoe

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

        canoe = CANoe.__new__(CANoe)
        canoe.application = app
        result = canoe.get_simulation_database_paths()
        assert result == ["C:/dbs/can.dbc"]

    def test_returns_empty_list_when_no_databases(self):
        bus_specs = [
            {"name": "CAN", "dbs": []},
            {"name": "LIN", "dbs": []},
        ]
        canoe = _make_canoe_with_sim_buses(bus_specs)
        result = canoe.get_simulation_database_paths()
        assert result == []

    def test_raises_on_exception(self):
        from py_canoe.canoe import CANoe

        app = MagicMock()
        type(app.configuration.simulation_setup).buses = PropertyMock(side_effect=Exception("COM error"))
        canoe = CANoe.__new__(CANoe)
        canoe.application = app
        with pytest.raises(ConfigurationNotLoadedError):
            canoe.get_simulation_database_paths()
