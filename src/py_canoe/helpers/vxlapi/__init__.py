"""Vector XL Driver Library -- zero-config Python wrapper.

Usage::

    from py_canoe.helpers.vxlapi import VxlDriver, XlBusType, HwType

    # List CAN channels
    for ch in VxlDriver().get_channels(XlBusType.CAN):
        print(ch.name)

    # Context manager (auto-open / close)
    with VxlDriver() as drv:
        drv.print_config()
        drv.set_appl_config("CANoe", 0, HwType.VN1630, 0, 1, XlBusType.CAN)
"""

from py_canoe.helpers.vxlapi.driver import VxlDriver
from py_canoe.helpers.vxlapi.enums import XlBusType, ChannelCapability, HwType
from py_canoe.helpers.vxlapi.types import ChannelInfo, DeviceInfo

__all__ = ["VxlDriver", "XlBusType", "HwType", "ChannelCapability", "ChannelInfo", "DeviceInfo"]
