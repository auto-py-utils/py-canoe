import sys
import pytest


def is_canoe_available() -> bool:
    """Check if CANoe COM interface is available."""
    if sys.platform != "win32":
        return False

    try:
        import pythoncom
        import win32com.client

        pythoncom.CoInitialize()
        canoe_app = win32com.client.Dispatch("CANoe.Application")
        del canoe_app
        pythoncom.CoUninitialize()
        return True
    except Exception:
        try:
            import pythoncom
            pythoncom.CoUninitialize()
        except Exception:
            pass
        return False


skip_if_no_canoe = pytest.mark.skipif(
    not is_canoe_available(),
    reason="CANoe requires Windows and COM interface"
)
