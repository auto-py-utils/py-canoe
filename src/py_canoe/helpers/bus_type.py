from enum import Enum

class BusType(Enum):
    CAN = 1
    J1939 = 2
    TTP = 4
    LIN = 5
    MOST = 6
    FlexRay = 7
    J1708 = 9
    Ethernet = 11
    WLAN = 13
    KLINE = 14