from py_canoe.core.com_session import dispatch_com_object


class Ports:
    """The Ports object represents all ports of a specific Ethernet bus in Network-based Access mode as a collection."""
    def __init__(self, ports_com_obj):
        self.com_object = dispatch_com_object(ports_com_obj)

    @property
    def count(self) -> int:
        return self.com_object.Count

    @property
    def is_port_based_config(self) -> bool:
        return self.com_object.IsPortBasedConfig

    @property
    def is_switched_network(self) -> bool:
        return self.com_object.IsSwitchedNetwork

    def item(self, index: int) -> 'Port':
        return Port(self.com_object.Item(index))

    @property
    def network_name(self) -> str:
        return self.com_object.NetworkName

    @property
    def ports_are_simulated(self) -> bool:
        return self.com_object.PortsAreSimulated

    @ports_are_simulated.getter
    def ports_are_simulated(self, value: bool):
        self.com_object.PortsAreSimulated = value

    def add(self, port_name: str, segment_name: str) -> 'Port':
        return Port(self.com_object.Add(port_name, segment_name))

    def add_mp(self, port_name: str) -> 'Port':
        return Port(self.com_object.AddMP(port_name))

    def remove(self, index: int):
        self.com_object.Remove(index)


class Port:
    """The Port object represents a specific port of a CANoe configuration."""
    def __init__(self, port_com_obj):
        self.com_object = dispatch_com_object(port_com_obj)

    @property
    def is_active(self) -> bool:
        return self.com_object.IsActive

    @is_active.setter
    def is_active(self, value: bool):
        self.com_object.IsActive = value

    @property
    def is_simulated(self) -> bool:
        return self.com_object.IsSimulated

    @is_simulated.setter
    def is_simulated(self, value: bool):
        self.com_object.IsSimulated = value

    @property
    def name(self) -> str:
        return self.com_object.Name

    @name.setter
    def name(self, value: str):
        self.com_object.Name = value

    @property
    def segment_name(self) -> str:
        return self.com_object.SegmentName

    @segment_name.setter
    def segment_name(self, value: str):
        self.com_object.SegmentName = value
