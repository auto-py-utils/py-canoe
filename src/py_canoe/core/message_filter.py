"""COM IMessageFilter to suppress 'Server Busy' dialogs.

When CANoe is busy (e.g., generating reports after measurement stop), COM calls
from Python may trigger a Windows dialog: "This action cannot be completed because
the other program is busy". This module provides an IMessageFilter implementation
that automatically retries rejected calls and suppresses the dialog.

The filter is registered per STA thread via CoRegisterMessageFilter. pythoncom
does not expose this API, so we use ctypes to build a proper COM vtable manually.
"""

import ctypes
import ctypes.wintypes
import logging

_logger = logging.getLogger("PY_CANOE")

# Load ole32.dll for CoRegisterMessageFilter
_ole32 = ctypes.windll.ole32
_CoRegisterMessageFilter = _ole32.CoRegisterMessageFilter
_CoRegisterMessageFilter.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
_CoRegisterMessageFilter.restype = ctypes.HRESULT

# IMessageFilter vtable callback signatures
_HANDLEINCOMINGCALL = ctypes.WINFUNCTYPE(
    ctypes.c_int,  # return: DWORD (SERVERCALL_*)
    ctypes.c_void_p,  # this
    ctypes.wintypes.DWORD,  # dwCallType
    ctypes.c_void_p,  # htaskCaller
    ctypes.wintypes.DWORD,  # dwTickCount
    ctypes.c_void_p,  # lpInterfaceInfo
)
_RETRYREJECTEDCALL = ctypes.WINFUNCTYPE(
    ctypes.c_int,  # return: DWORD (milliseconds to wait, or -1 to cancel)
    ctypes.c_void_p,  # this
    ctypes.c_void_p,  # htaskCallee
    ctypes.wintypes.DWORD,  # dwTickCount
    ctypes.wintypes.DWORD,  # dwRejectType
)
_MESSAGEPENDING = ctypes.WINFUNCTYPE(
    ctypes.c_int,  # return: DWORD (PENDINGMSG_*)
    ctypes.c_void_p,  # this
    ctypes.c_void_p,  # htaskCallee
    ctypes.wintypes.DWORD,  # dwTickCount
    ctypes.wintypes.DWORD,  # dwPendingType
)


class _IMessageFilterVtbl(ctypes.Structure):
    """COM vtable layout for IMessageFilter."""

    _fields_ = [
        ("QueryInterface", ctypes.c_void_p),
        ("AddRef", ctypes.c_void_p),
        ("Release", ctypes.c_void_p),
        ("HandleInComingCall", ctypes.c_void_p),
        ("RetryRejectedCall", ctypes.c_void_p),
        ("MessagePending", ctypes.c_void_p),
    ]


class _IMessageFilterImpl(ctypes.Structure):
    """COM object layout: pointer to vtable."""

    _fields_ = [("lpVtbl", ctypes.POINTER(_IMessageFilterVtbl))]


class COMRetryMessageFilter:
    """IMessageFilter that retries rejected COM calls and suppresses 'Server Busy' dialogs.

    Usage:
        filter = COMRetryMessageFilter()
        filter.register()
        # ... COM calls are now protected ...
        # filter.unregister()  # optional, usually kept active for app lifetime

    The filter uses exponential backoff for retries:
    - 0-1s: retry every 100ms
    - 1-5s: retry every 500ms
    - 5-30s: retry every 2s
    - 30-60s: retry every 5s
    - >60s: give up (cancel call)
    """

    _CANCEL_CALL = 0xFFFFFFFF  # -1 as DWORD

    def __init__(self) -> None:
        self._last_log_time = 0
        self._rejection_count = 0
        self._old_filter = ctypes.c_void_p()
        self._registered = False

        # IUnknown stubs — COM does not call these for message filters
        _qi_type = ctypes.WINFUNCTYPE(
            ctypes.HRESULT, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p
        )
        _ref_type = ctypes.WINFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p)
        self._qi = _qi_type(lambda this, riid, ppv: 0x80004002)  # E_NOINTERFACE
        self._addref = _ref_type(lambda this: 1)
        self._release = _ref_type(lambda this: 1)

        # IMessageFilter callbacks — prevent GC by storing on self
        self._cb_handle = _HANDLEINCOMINGCALL(self._on_handle_incoming)
        self._cb_retry = _RETRYREJECTEDCALL(self._on_retry_rejected)
        self._cb_pending = _MESSAGEPENDING(self._on_message_pending)

        self._vtbl = _IMessageFilterVtbl(
            QueryInterface=ctypes.cast(self._qi, ctypes.c_void_p).value,
            AddRef=ctypes.cast(self._addref, ctypes.c_void_p).value,
            Release=ctypes.cast(self._release, ctypes.c_void_p).value,
            HandleInComingCall=ctypes.cast(self._cb_handle, ctypes.c_void_p).value,
            RetryRejectedCall=ctypes.cast(self._cb_retry, ctypes.c_void_p).value,
            MessagePending=ctypes.cast(self._cb_pending, ctypes.c_void_p).value,
        )
        self._impl = _IMessageFilterImpl(lpVtbl=ctypes.pointer(self._vtbl))
        self._ptr = ctypes.cast(ctypes.pointer(self._impl), ctypes.c_void_p)

    def register(self) -> None:
        """Register this filter on the current STA thread.

        Silently skips registration if COM is not initialized (e.g., in unit tests).
        This is safe because the filter only provides enhanced behavior (dialog
        suppression) — code works correctly without it, just with potential dialogs.
        """
        if self._registered:
            return
        try:
            hr = _CoRegisterMessageFilter(self._ptr, ctypes.byref(self._old_filter))
            if hr != 0:
                _logger.debug(f"CoRegisterMessageFilter returned HRESULT=0x{hr:08X} — filter not active")
            else:
                self._registered = True
                _logger.debug("IMessageFilter registered — 'Server Busy' dialogs suppressed")
        except OSError as e:
            # COM not initialized (e.g., unit tests without STA) — skip silently
            _logger.debug(f"CoRegisterMessageFilter skipped (COM not initialized): {e}")

    def unregister(self) -> None:
        """Unregister this filter and restore the previous one."""
        if not self._registered:
            return
        _CoRegisterMessageFilter(self._old_filter, ctypes.byref(ctypes.c_void_p()))
        self._registered = False
        _logger.debug("IMessageFilter unregistered")

    def _on_handle_incoming(
        self, this, dwCallType, htaskCaller, dwTickCount, lpInterfaceInfo
    ) -> int:
        return 0  # SERVERCALL_ISHANDLED

    def _on_retry_rejected(
        self, this, htaskCallee, dwTickCount, dwRejectType
    ) -> int:
        self._rejection_count += 1

        # Log at key intervals
        if dwTickCount == 0:
            _logger.warning(f"COM call rejected — starting retry (type={dwRejectType})")
        elif dwTickCount >= 1000 and self._last_log_time < 1000:
            _logger.warning(f"COM call still busy after 1s (retries={self._rejection_count})")
        elif dwTickCount >= 5000 and self._last_log_time < 5000:
            _logger.warning(f"COM call still busy after 5s (retries={self._rejection_count})")
        elif dwTickCount >= 30000 and self._last_log_time < 30000:
            _logger.warning(f"COM call still busy after 30s (retries={self._rejection_count})")
        self._last_log_time = dwTickCount

        # Only retry for SERVERCALL_REJECTED (1) or SERVERCALL_RETRYLATER (2)
        if dwRejectType not in (1, 2):
            return self._CANCEL_CALL

        # Exponential backoff
        if dwTickCount < 1000:
            return 100
        elif dwTickCount < 5000:
            return 500
        elif dwTickCount < 30000:
            return 2000
        elif dwTickCount < 60000:
            return 5000
        else:
            _logger.error(
                f"COM call timeout after 60s — giving up (retries={self._rejection_count})"
            )
            return self._CANCEL_CALL

    def _on_message_pending(self, this, htaskCallee, dwTickCount, dwPendingType) -> int:
        return 1  # PENDINGMSG_WAITNOPROCESS (suppress "Server Busy" dialog)
