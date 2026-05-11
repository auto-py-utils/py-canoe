import pytest
import pythoncom


def is_canoe_available() -> bool:
    """Check if CANoe COM interface is available."""
    try:
        pythoncom.CoInitialize()
        import win32com.client
        canoe_app = win32com.client.Dispatch("CANoe.Application")
        del canoe_app
        pythoncom.CoUninitialize()
        return True
    except Exception:
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass
        return False


skip_if_no_canoe = pytest.mark.skipif(
    not is_canoe_available(),
    reason="CANoe COM interface not available"
)
