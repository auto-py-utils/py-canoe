from py_canoe.core.child_elements.modules import Modules
from py_canoe.core.child_elements.signals import Signals
from py_canoe.core.com_session import dispatch_com_object


class Nodes:
    """The Nodes object represents all nodes of the Simulation Setup / System and Communication Setup of the CANoe application."""
    def __init__(self, nodes_com_obj):
        self.com_object = nodes_com_obj

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int) -> 'Node':
        return Node(self.com_object.Item(index))

    def add(self, name: str) -> 'Node':
        return Node(self.com_object.Add(name))

    def add_test_module_ex(self, name:str, type: int) -> 'Node':
        return Node(self.com_object.AddTestModuleEx(name, type))

    def add_with_title(self, name: str) -> 'Node':
        return Node(self.com_object.AddWithTitle(name))

    def add_test_module(self, name: str) -> 'Node':
        return Node(self.com_object.AddTestModule(name))

    def remove(self, index: int):
        self.com_object.Remove(index)


class Node:
    """The Node object represents a node of the Simulation Setup / System and Communication Setup of the CANoe application."""
    def __init__(self, node_com_obj):
        self.com_object = dispatch_com_object(node_com_obj)

    @property
    def active(self) -> bool:
        return self.com_object.Active

    @property
    def full_name(self) -> str:
        return self.com_object.FullName

    @property
    def inputs(self) -> 'Signals':
        return Signals(self.com_object.Inputs)

    @property
    def is_gateway(self) -> bool:
        return self.com_object.IsGateway

    @property
    def modules(self) -> 'Modules':
        return Modules(self.com_object.Modules)

    @property
    def name(self) -> str:
        return self.com_object.Name

    @property
    def outputs(self) -> 'Signals':
        return Signals(self.com_object.Outputs)

    @property
    def path(self) -> str:
        return self.com_object.Path

    @property
    def port_creation(self) -> int:
        return self.com_object.PortCreation

    @port_creation.setter
    def port_creation(self, value: int):
        self.com_object.PortCreation = value

    @property
    def start_delay(self) -> int:
        return self.com_object.StartDelay

    @start_delay.setter
    def start_delay(self, value: int):
        self.com_object.StartDelay = value

    @property
    def start_delay_active(self) -> bool:
        return self.com_object.StartDelayActive

    @start_delay_active.setter
    def start_delay_active(self, value: bool):
        self.com_object.StartDelayActive = value

    @property
    def start_delay_from_db(self) -> bool:
        return self.com_object.StartDelayFromDb

    @start_delay_from_db.setter
    def start_delay_from_db(self, value: bool):
        self.com_object.StartDelayFromDb = value

    @property
    def tcp_ip_stack_setting(self):
        return self.com_object.TcpIpStackSetting

    @property
    def test_module(self) -> bool:
        return self.com_object.TestModule

    def attach_bus(self, bus_com_obj):
        self.com_object.AttachBus(bus_com_obj)

    def detach_bus(self, bus_com_obj):
        self.com_object.DetachBus(bus_com_obj)

    def is_bus_attached(self, bus_com_obj) -> bool:
        return self.com_object.IsBusAttached(bus_com_obj)
