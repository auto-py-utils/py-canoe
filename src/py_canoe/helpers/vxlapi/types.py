"""Lightweight data classes for hardware query results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List

from py_canoe.helpers.vxlapi.enums import XlBusType

if TYPE_CHECKING:
    from py_canoe.helpers.vxlapi.driver import VxlDriver


@dataclass
class ChannelInfo:
    """A single hardware channel discovered by the XL Driver."""

    name: str
    hw_type: int
    hw_index: int
    hw_channel: int
    channel_index: int
    channel_mask: int
    transceiver_name: str
    transceiver_type: int
    serial_number: int
    article_number: int
    is_on_bus: bool
    connected_bus_type: int
    bus_capabilities: int
    channel_capabilities: int

    # -- back-reference to driver (set by VxlDriver) --
    _driver: object = field(default=None, repr=False, compare=False)

    def supports(self, bus: XlBusType) -> bool:
        """Return *True* if this channel can handle *bus*."""
        return bool(self.bus_capabilities & bus.value)

    # -- convenience properties --
    @property
    def can(self) -> bool:      return self.supports(XlBusType.CAN)
    @property
    def lin(self) -> bool:      return self.supports(XlBusType.LIN)
    @property
    def flexray(self) -> bool:  return self.supports(XlBusType.FLEXRAY)
    @property
    def ethernet(self) -> bool: return self.supports(XlBusType.ETHERNET)

    # -- apply this channel to an app --
    def apply_to(self, app: str, app_ch: int, bus: XlBusType = XlBusType.NONE) -> None:
        """Map *app*'s logical channel *app_ch* to this physical channel.

        Example::

            ch.apply_to("CANoe", 0, XlBusType.CAN)
        """
        from py_canoe.helpers.vxlapi.driver import VxlDriver
        drv = self._driver if isinstance(self._driver, VxlDriver) else VxlDriver()
        drv.set_appl_config(app, app_ch, self, bus)
        if not isinstance(self._driver, VxlDriver):
            drv.close()

    @property
    def label(self) -> str:
        """Human-readable one-line summary."""
        return f"Ch{self.hw_channel:02d} idx={self.channel_index} [{self.transceiver_name}]"


@dataclass
class DeviceInfo:
    """A hardware device with its channels."""

    name: str
    hw_type: int
    hw_index: int
    serial_number: int
    article_number: int
    channels: List[ChannelInfo] = field(default_factory=list)
