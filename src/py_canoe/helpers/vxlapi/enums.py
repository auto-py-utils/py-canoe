"""Vector XL Driver Library constants as Python Enums.

All bus types and hardware types are defined here so that callers never
need to pass raw integer "magic values" into driver methods.
"""

from enum import IntEnum, IntFlag


class XlBusType(IntEnum):
    """Bus system types (from ``XL_BUS_TYPE_*`` in vxlapi.h)."""

    NONE = 0x00000000
    CAN = 0x00000001
    LIN = 0x00000002
    FLEXRAY = 0x00000004
    AFDX = 0x00000008
    MOST = 0x00000010
    DAIO = 0x00000040
    J1708 = 0x00000100
    KLINE = 0x00000800
    ETHERNET = 0x00001000
    A429 = 0x00002000
    STATUS = 0x00020000


class HwType(IntEnum):
    """Hardware device types (from ``XL_HWTYPE_*`` in vxlapi.h)."""

    NONE = 0
    VIRTUAL = 1
    CANCARDX = 2
    CANCARDXL = 15
    CANCASEXL = 21
    VN8900 = 45
    VN1610 = 55
    VN1630 = 57
    VN1640 = 59
    VN5610 = 65
    VN7610 = 81
    VN5610A = 101
    VN7640 = 102
    VN1670 = 115


class ChannelCapability(IntFlag):
    """Channel capability flags (from ``XL_CHANNEL_FLAG_EX1_*``)."""

    CANFD_ISO_SUPPORT = 0x40000
