import win32com.client

from py_canoe.core.child_elements.ccp_setup import CCPSetup
from py_canoe.core.child_elements.can_controller import CanController
from py_canoe.core.child_elements.database_setup import DatabaseSetup
from py_canoe.core.child_elements.diagnostics_setup import DiagnosticsSetup
from py_canoe.core.child_elements.macros_setup import MacrosSetup
from py_canoe.core.child_elements.panel_setup import PanelSetup
from py_canoe.core.child_elements.security_setup import SecuritySetup
from py_canoe.core.child_elements.snippet_setup import SnippetSetup
from py_canoe.core.child_elements.visual_sequence_setup import VisualSequenceSetup
from py_canoe.core.child_elements.xcp_setup import XCPSetup
from py_canoe.helpers.bus_type import BusType


class GeneralSetup:
    """
    The MeasurementSetup object rRepresents the general settings of a CANoe configuration.
    """
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def ccp_setup(self) -> 'CCPSetup':
        return CCPSetup(self.com_object.CCPSetup)

    def get_channels_count(self, bus_type: BusType) -> int:
        """Returns the number of channels of the given bus type.

        Args:
            bus_type (BusType): The bus type (e.g. BusType.CAN).

        Returns:
            int: The number of channels.
        """
        return self.com_object.Channels(bus_type.value)

    def set_channels_count(self, bus_type: BusType, channel: int) -> None:
        """Sets the number of channels of the given bus type.

        Args:
            bus_type (BusType): The bus type (e.g. BusType.CAN).
            channel (int): The number of channels to set.
        """
        self.com_object.SetChannels(bus_type.value, channel)

    def controller_setup(self, bus_type: BusType, channel: int) -> 'CanController':
        """Returns the CanController object for the given bus type and channel.

        Args:
            bus_type (BusType): The bus type (e.g. BusType.CAN).
            channel (int): The channel number.

        Returns:
            CanController: The controller setup object.
        """
        return CanController(self.com_object.ControllerSetup(bus_type.value, channel))

    @property
    def database_setup(self) -> 'DatabaseSetup':
        return DatabaseSetup(self.com_object.DatabaseSetup)

    @property
    def diagnostics_setup(self) -> 'DiagnosticsSetup':
        return DiagnosticsSetup(self.com_object.DiagnosticsSetup)

    @property
    def macros_setup(self) -> 'MacrosSetup':
        return MacrosSetup(self.com_object.MacrosSetup)

    @property
    def panel_setup(self) -> 'PanelSetup':
        return PanelSetup(self.com_object.PanelSetup)

    @property
    def security_setup(self) -> 'SecuritySetup':
        return SecuritySetup(self.com_object.SecuritySetup)

    @property
    def snippet_setup(self) -> 'SnippetSetup':
        return SnippetSetup(self.com_object.SnippetSetup)

    @property
    def visual_sequence_setup(self) -> 'VisualSequenceSetup':
        return VisualSequenceSetup(self.com_object.VisualSequenceSetup)

    @property
    def xcp_setup(self) -> 'XCPSetup':
        return XCPSetup(self.com_object.XCPSetup)
