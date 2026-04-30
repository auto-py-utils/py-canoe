from unittest.mock import MagicMock, PropertyMock
from py_canoe.core.networks import Networks


class TestGetAllNetworkNames:
    def _make_networks(self, names):
        com = MagicMock()
        com.Count = len(names)

        def item_side_effect(index):
            net = MagicMock()
            net.Name = names[index - 1]
            return net

        com.Item.side_effect = item_side_effect
        networks = Networks.__new__(Networks)
        networks.com_object = com
        networks.diagnostic_devices = {}
        return networks

    def test_returns_all_names(self):
        networks = self._make_networks(["CAN_1", "LIN_1", "Ethernet_1"])
        result = networks.get_all_network_names()
        assert result == ["CAN_1", "LIN_1", "Ethernet_1"]

    def test_includes_empty_string_names(self):
        networks = self._make_networks(["CAN_1", "", "LIN_1"])
        result = networks.get_all_network_names()
        assert result == ["CAN_1", "", "LIN_1"]

    def test_skips_none_names(self):
        com = MagicMock()
        com.Count = 2

        def item_side_effect(index):
            net = MagicMock()
            net.Name = None if index == 1 else "CAN_1"
            return net

        com.Item.side_effect = item_side_effect
        networks = Networks.__new__(Networks)
        networks.com_object = com
        networks.diagnostic_devices = {}
        result = networks.get_all_network_names()
        assert result == ["CAN_1"]

    def test_returns_empty_list_when_no_networks(self):
        networks = self._make_networks([])
        result = networks.get_all_network_names()
        assert result == []

    def test_returns_empty_list_on_exception(self):
        com = MagicMock()
        type(com).Count = PropertyMock(side_effect=Exception("COM error"))
        networks = Networks.__new__(Networks)
        networks.com_object = com
        networks.diagnostic_devices = {}
        result = networks.get_all_network_names()
        assert result == []
