"""Vector XL Driver Library -- zero-config Python wrapper.

Usage::

    from py_canoe.helpers.vxlapi import VxlDriver, XlBusType, HwType

    # One-liner: get all CAN hardware channels
    for ch in VxlDriver().get_channels(XlBusType.CAN):
        print(ch.name)

    # Context manager:
    with VxlDriver() as drv:
        drv.print_config()
        drv.set_appl_config("CANoe", 0, HwType.VN1630, 0, 1, XlBusType.CAN)
"""

from __future__ import annotations

import atexit
import ctypes
import os
import struct
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from py_canoe.helpers.common import logger
from py_canoe.helpers.vxlapi.enums import HwType, XlBusType
from py_canoe.helpers.vxlapi.types import ChannelInfo, DeviceInfo

# ---------------------------------------------------------------------------
# internal ctypes (mirrors vxlapi.h, not exported)
# ---------------------------------------------------------------------------

def _from_cstr(buf: bytes) -> str:
    return buf.decode("utf-8", errors="replace").rstrip("\x00")

_UI16 = ctypes.c_uint16
_UI32 = ctypes.c_uint32
_UI64 = ctypes.c_uint64
_BYTE = ctypes.c_ubyte
_CHAR = ctypes.c_char

class _BusCan(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("bitRate", _UI32), ("sjw", _BYTE), ("tseg1", _BYTE), ("tseg2", _BYTE),
        ("sam", _BYTE), ("outputMode", _BYTE), ("_pad", _BYTE * 7), ("canOpMode", _BYTE),
    ]

class _BusCanFd(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("arb_bitRate", _UI32), ("sjwAbr", _BYTE), ("tseg1Abr", _BYTE), ("tseg2Abr", _BYTE),
        ("samAbr", _BYTE), ("outputMode", _BYTE),
        ("sjwDbr", _BYTE), ("tseg1Dbr", _BYTE), ("tseg2Dbr", _BYTE),
        ("dataBitRate", _UI32), ("canOpMode", _BYTE),
    ]

class _BusData(ctypes.Union):
    _pack_ = 1
    _fields_ = [("can", _BusCan), ("canFd", _BusCanFd), ("raw", _BYTE * 28)]

class _BusParams(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("busType", _UI32), ("data", _BusData)]

class _ChCfg(ctypes.Structure):
    """XL_CHANNEL_CONFIG -- 1-byte packed (matches vxlapi.h ``#pragma pack(1)``)."""
    _pack_ = 1
    _fields_ = [
        ("name",                       _CHAR * 32),
        ("hwType",                     _BYTE),
        ("hwIndex",                    _BYTE),
        ("hwChannel",                  _BYTE),
        ("transceiverType",            _UI16),
        ("transceiverState",           _UI16),
        ("configError",                _UI16),
        ("channelIndex",               _BYTE),
        ("channelMask",                _UI64),
        ("channelCapabilities",        _UI32),
        ("channelBusCapabilities",     _UI32),
        ("isOnBus",                    _BYTE),
        ("connectedBusType",           _UI32),
        ("busParams",                  _BusParams),
        ("_doNotUse",                  _UI32),
        ("driverVersion",              _UI32),
        ("interfaceVersion",           _UI32),
        ("raw_data",                   _UI32 * 10),
        ("serialNumber",               _UI32),
        ("articleNumber",              _UI32),
        ("transceiverName",            _CHAR * 32),
        ("specialCabFlags",            _UI32),
        ("dominantTimeout",            _UI32),
        ("dominantRecessiveDelay",     _BYTE),
        ("recessiveDominantDelay",     _BYTE),
        ("connectionInfo",             _BYTE),
        ("currentlyAvailableTimestamps", _BYTE),
        ("minimalSupplyVoltage",       _UI16),
        ("maximalSupplyVoltage",       _UI16),
        ("maximalBaudrate",            _UI32),
        ("fpgaCoreCapabilities",       _BYTE),
        ("specialDeviceStatus",        _BYTE),
        ("channelBusActiveCapabilities", _UI16),
        ("breakOffset",                _UI16),
        ("delimiterOffset",            _UI16),
        ("reserved",                   _UI32 * 3),
    ]

class _DrvCfg(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("dllVersion", _UI32), ("channelCount", _UI32),
        ("_reserved", _UI32 * 10), ("channel", _ChCfg * 64),
    ]


# ---------------------------------------------------------------------------
# DLL loading 鈥?automatic, once-only, releases on exit
# ---------------------------------------------------------------------------

_DLL: Optional[ctypes.CDLL] = None
_OPEN_COUNT: int = 0

def _find_dll() -> Path:
    """Locate the right vxlapi DLL for this Python process."""
    is64 = struct.calcsize("P") == 8
    name = "vxlapi64.dll" if is64 else "vxlapi.dll"

    # 1) bundled bin/ directory
    bundled = Path(__file__).resolve().parent / "bin" / name
    if bundled.exists():
        return bundled

    # 2) VXLAPI_DLL_PATH env var
    env = os.environ.get("VXLAPI_DLL_PATH")
    if env:
        p = Path(env) / name if Path(env).is_dir() else Path(env)
        if p.exists():
            return p

    # 3) Public Vector installation
    base = Path(os.environ.get("PUBLIC", r"C:\Users\Public")) / "Documents" / "Vector"
    for d in sorted(base.glob("XL Driver Library*"), reverse=True):
        p = d / "bin" / name
        if p.exists():
            return p

    # 4) PATH fallback
    return Path(name)

def _get_dll() -> ctypes.CDLL:
    """Return the loaded DLL (singleton), raising if unavailable."""
    global _DLL
    if _DLL is not None:
        return _DLL
    path = _find_dll()
    logger.info("Loading %s", path)
    _DLL = ctypes.CDLL(str(path))
    return _DLL

def _open() -> None:
    global _OPEN_COUNT
    if _OPEN_COUNT == 0:
        if _get_dll().xlOpenDriver() != 0:
            raise RuntimeError("xlOpenDriver failed")
    _OPEN_COUNT += 1

def _close() -> None:
    global _OPEN_COUNT, _DLL
    if _OPEN_COUNT > 0:
        _OPEN_COUNT -= 1
    if _OPEN_COUNT == 0 and _DLL is not None:
        _DLL.xlCloseDriver()
        _DLL = None

atexit.register(_close)


# ---------------------------------------------------------------------------
# Public class
# ---------------------------------------------------------------------------

class VxlDriver:
    """Enumerate Vector hardware and manage app-channel mappings.

    The underlying DLL is loaded & opened on first use and
    released automatically when all instances are closed (or at exit).
    """

    def __init__(self):
        _open()

    # -- context manager ---------------------------------------------------
    def __enter__(self) -> VxlDriver:
        return self

    def __exit__(self, *a) -> None:
        self.close()

    def close(self) -> None:
        _close()

    # -- channels ----------------------------------------------------------

    def get_devices(self) -> List[DeviceInfo]:
        """Return all Vector devices with their channels."""
        dll = _get_dll()
        cfg = _DrvCfg()
        if dll.xlGetDriverConfig(ctypes.byref(cfg)) != 0:
            raise RuntimeError("xlGetDriverConfig failed")

        devs: Dict[Tuple[int, int], DeviceInfo] = {}
        for i in range(cfg.channelCount):
            c = cfg.channel[i]
            key = (c.hwType, c.hwIndex)
            if key not in devs:
                devs[key] = DeviceInfo(
                    name=_from_cstr(c.name).rsplit(" ", 1)[0],
                    hw_type=c.hwType, hw_index=c.hwIndex,
                    serial_number=c.serialNumber, article_number=c.articleNumber,
                )
            ch = ChannelInfo(
                name=_from_cstr(c.name),
                hw_type=c.hwType, hw_index=c.hwIndex, hw_channel=c.hwChannel,
                channel_index=c.channelIndex, channel_mask=c.channelMask,
                transceiver_name=_from_cstr(c.transceiverName),
                transceiver_type=c.transceiverType,
                serial_number=c.serialNumber, article_number=c.articleNumber,
                is_on_bus=bool(c.isOnBus), connected_bus_type=c.connectedBusType,
                bus_capabilities=c.channelBusCapabilities, channel_capabilities=c.channelCapabilities,
            )
            ch._driver = self  # enable ch.apply_to(...)
            devs[key].channels.append(ch)
        return list(devs.values())

    def get_channels(self, bus: XlBusType | None = None) -> List[ChannelInfo]:
        """Return channels, optionally filtered by bus type."""
        return [ch for dev in self.get_devices()
                for ch in dev.channels
                if bus is None or ch.supports(bus)]

    def print_config(self) -> None:
        """Print hardware overview to log."""
        devs = self.get_devices()
        logger.info("%d devices, %d channels", len(devs), sum(len(d.channels) for d in devs))
        for d in devs:
            hw_name = HwType(d.hw_type).name if d.hw_type in (m.value for m in HwType) else f"UNKNOWN({d.hw_type})"
            logger.info("  %s  SN=%08X  type=%s", d.name, d.serial_number, hw_name)
            for c in d.channels:
                tags = [b.name for b in (XlBusType.CAN, XlBusType.LIN, XlBusType.ETHERNET, XlBusType.FLEXRAY) if c.supports(b)]
                logger.info("    Ch%02d  idx=%d  0x%X  [%s]  %s",
                            c.hw_channel, c.channel_index, c.channel_mask,
                            " | ".join(tags), c.transceiver_name)

    # -- app config --------------------------------------------------------

    def get_appl_config(self, app: str, ch: int,
                        bus: XlBusType = XlBusType.NONE) -> ChannelInfo | None:
        """Return the :class:`ChannelInfo` mapped to *app* channel *ch*,
        or *None* if not configured."""
        dll = _get_dll()
        a, b, c = (_UI32(), _UI32(), _UI32())
        if dll.xlGetApplConfig(app.encode(), ch,
                               ctypes.byref(a), ctypes.byref(b), ctypes.byref(c), bus.value):
            return None
        for dev in self.get_devices():
            for hw_ch_info in dev.channels:
                if hw_ch_info.hw_type == a.value and hw_ch_info.hw_index == b.value \
                        and hw_ch_info.hw_channel == c.value:
                    return hw_ch_info
        return None

    def set_appl_config(self, app: str, ch: int,
                        hw: HwType | ChannelInfo,
                        hw_idx: int = 0, hw_ch: int = 0,
                        bus: XlBusType = XlBusType.NONE) -> None:
        """Map *app* channel *ch* to physical hardware.

        *hw* can be a :class:`HwType` + explicit *hw_idx*/*hw_ch*,
        or a :class:`ChannelInfo` from :meth:`get_channels` (simplest).

        Examples::

            drv.set_appl_config("CANoe", 0, hw_chan, bus=XlBusType.CAN)   # from query
            drv.set_appl_config("CANoe", 0, HwType.VN1630, 0, 1, XlBusType.CAN)  # manual
        """
        if isinstance(hw, ChannelInfo):
            hw_type = hw.hw_type
            hw_idx, hw_ch = hw.hw_index, hw.hw_channel
        else:
            hw_type = hw.value
        dll = _get_dll()
        if dll.xlSetApplConfig(app.encode(), ch, int(hw_type), hw_idx, hw_ch, bus.value):
            raise RuntimeError(f"xlSetApplConfig({app!r}, ch={ch}) failed")
        logger.info("%s ch%d --> hw(%d,%d,%d) [%s]", app, ch,
                    int(hw_type), hw_idx, hw_ch,
                    hw.transceiver_name if isinstance(hw, ChannelInfo) else HwType(hw_type).name)

    def unset_appl_config(self, app: str, ch: int) -> None:
        """Remove the hardware mapping for *app* channel *ch*.

        Sets it to HwType.NONE / index 0 / channel 0 / BusType.NONE.
        """
        self.set_appl_config(app, ch, HwType.NONE, 0, 0, XlBusType.NONE)

    def unset_all_appl_config(self, app: str,
                              max_channels: int = 16) -> None:
        """Clear hardware mappings for all channels of *app*.

        Scans channels 0..*max_channels*-1; only unmaps configured ones."""
        count = 0
        for ch in range(max_channels):
            if self.get_appl_config(app, ch) is not None:
                self.unset_appl_config(app, ch)
                count += 1
        logger.info("Cleared %d channel(s) for %s", count, app)

    # -- channel index / mask ----------------------------------------------

    def get_channel_index(self, hw: HwType | None = None,
                          hw_idx: int = -1, hw_ch: int = -1) -> int:
        dll = _get_dll()
        return dll.xlGetChannelIndex(hw.value if hw else -1, hw_idx, hw_ch)

    def get_channel_mask(self, hw: HwType | None = None,
                         hw_idx: int = -1, hw_ch: int = -1) -> int:
        dll = _get_dll()
        return dll.xlGetChannelMask(hw.value if hw else -1, hw_idx, hw_ch)
