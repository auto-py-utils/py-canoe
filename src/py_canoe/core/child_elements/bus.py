import win32com.client

from py_canoe.core.child_elements.channels import Channels
from py_canoe.core.child_elements.databases import Databases
from py_canoe.core.child_elements.nodes import Nodes
from py_canoe.core.child_elements.ports import Ports
from py_canoe.core.child_elements.replay_collection import ReplayCollection
from py_canoe.core.child_elements.security_configuration import SecurityConfiguration
from py_canoe.core.child_elements.signals import Signal


class _EmptyComCollection:
    """Fallback collection used when a CANoe bus interface does not expose optional members."""

    Count = 0

    def Item(self, index: int):
        raise IndexError(index)


class Bus:
    """The Bus object represents a bus of your application.

    The instantiation of the Bus object is done by the Bus property of the
    Application object or by the Buses collection of the Simulation Setup.

    Properties:
        active: Sets or returns the status of the Bus object.
        channels: Returns the Channels object (read-only).
        databases: Returns the Databases object (read-only).
        generators: Returns the Generators object (read-only).
        interactive_generators: Returns the InteractiveGenerators object (read-only).
        name: Sets or returns the name of the bus.
        nodes: Returns the Nodes object (read-only).
        ports: Returns the collection of Ports (read-only).
        replay_collection: Returns the ReplayCollection object (read-only).
        security_configuration: Returns the SecurityConfiguration (read-only).

    Methods:
        autogenerate_nodes: Automatically generates network nodes based on the
                            first assigned database (LIN buses only).
        get_signal: Returns a Signal object.
        get_j1939_signal: Returns a Signal object for J1939 buses.
    """

    __test__ = False

    def __init__(self, com_object):
        """The Bus object wraps a COM Bus object.

        Args:
            com_object: The COM Bus object (e.g. obtained from
                        ``app.com_object.GetBus(<bus-name>)`` or ``buses.Item(i)``).
        """
        self.com_object = com_object
        self.VALUE_TABLE_SIGNAL_IS_ONLINE = {
            True: "measurement is running and the signal has been received.",
            False: "The signal is not online."
        }
        self.VALUE_TABLE_SIGNAL_STATE = {
            0: "The default value of the signal is returned.",
            1: "The measurement is not running. The value set by the application is returned.",
            2: "The measurement is not running. The value of the last measurement is returned.",
            3: "The signal has been received in the current measurement. The current value is returned."
        }

    @property
    def active(self) -> bool:
        """Sets or returns the status of the Bus object (whether the bus is simulated)."""
        return self.com_object.Active

    @active.setter
    def active(self, value: bool) -> None:
        self.com_object.Active = value

    @property
    def channels(self) -> Channels:
        """Returns the Channels object associated with the bus."""
        channels_com = getattr(self.com_object, 'Channels', None)
        if channels_com is None:
            return Channels(_EmptyComCollection())
        return Channels(channels_com)

    @property
    def databases(self) -> Databases:
        """Returns the Databases object of the bus."""
        databases_com = getattr(self.com_object, 'Databases', None)
        if databases_com is None:
            return Databases(_EmptyComCollection())
        return Databases(databases_com)

    @property
    def generators(self):
        """Returns the Generators object of the bus."""
        return self.com_object.Generators

    @property
    def interactive_generators(self):
        """Returns the InteractiveGenerators object of the bus."""
        return self.com_object.InteractiveGenerators

    @property
    def name(self) -> str:
        """Sets or returns the name of the bus."""
        return getattr(self.com_object, 'Name', None)

    @name.setter
    def name(self, value: str) -> None:
        if hasattr(self.com_object, 'Name'):
            self.com_object.Name = value

    @property
    def nodes(self) -> Nodes:
        """Returns the Nodes object of the bus."""
        return Nodes(self.com_object.Nodes)

    @property
    def ports(self) -> Ports:
        """Returns the collection of Ports."""
        return Ports(self.com_object.Ports)

    @property
    def replay_collection(self) -> ReplayCollection:
        """Returns the ReplayCollection object of the bus."""
        return ReplayCollection(self.com_object.ReplayCollection)

    @property
    def security_configuration(self) -> SecurityConfiguration:
        """Returns the SecurityConfiguration of the bus."""
        return SecurityConfiguration(self.com_object.SecurityConfiguration)

    def autogenerate_nodes(self) -> None:
        """Automatically generates network nodes based on the first assigned database.

        The function is restricted to LIN buses.
        """
        self.com_object.AutogenerateNodes()

    def get_signal(self, channel: int, message: str, signal: str) -> Signal:
        """Returns a Signal object.

        Args:
            channel: The channel on which the signal is sent.
                     -1 or 0 is the wildcard for the channel selection.
            message: The name of the message to which the signal belongs.
            signal: The name of the signal.

        Returns:
            The Signal object.
        """
        return Signal(self.com_object.GetSignal(channel, message, signal))

    def get_j1939_signal(self, channel: int, message: str, signal: str,
                         source_addr: int, dest_addr: int) -> Signal:
        """Returns a Signal object for a J1939 bus.

        Args:
            channel: The channel on which the signal is sent.
            message: The name of the message to which the signal belongs.
            signal: The name of the signal.
            source_addr: The source address of the ECU that sends the message.
            dest_addr: The destination address of the ECU that receives the message.

        Returns:
            The Signal object.
        """
        return Signal(self.com_object.GetJ1939Signal(channel, message, signal, source_addr, dest_addr))
