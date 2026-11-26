import sys

import pytest


def is_canoe_available() -> bool:
    """Check if CANoe COM interface is available."""
    if sys.platform != "win32":
        return False

    try:
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_CLASSES_ROOT, r"CANoe.Application\CLSID"
        ) as key:
            winreg.QueryValueEx(key, "")
        return True
    except OSError:
        return False


skip_if_no_canoe = pytest.mark.skipif(not is_canoe_available(), reason="CANoe requires Windows and COM interface")
