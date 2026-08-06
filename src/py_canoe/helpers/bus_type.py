from enum import Enum


class BusType(Enum):
    """CANoe bus types aligned with the official COM ``eBusType`` enumeration.

    Reference: ``<CANoe install>/Exec32/COMdev/CANoe.h`` (eBusType).

    Note:
        - ``WLAN`` (13) is reused by the Car2x / "Ath" WLAN hardware interface
          (see CANoe help ``car2xHwConfigPageAth.htm``: "Network Hardware
          Configuration - Ath (Car2x)" configures the WLAN device used by
          Car2x).
        - ``J1939`` has no dedicated ``eBusType`` value; it runs on CAN
          channels.
    """

    CAN = 1
    J1939 = 2  # no dedicated eBusType; runs on CAN channels
    TTP = 4
    LIN = 5
    MOST = 6
    FlexRay = 7
    J1708 = 9
    Ethernet = 11
    WLAN = 13  # reused by Car2x / "Ath" WLAN interface
    AFDX = 14
    KLINE = 15
    A429 = 16