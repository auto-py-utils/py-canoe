"""Unit tests for COMRetryMessageFilter."""

import ctypes
from unittest.mock import MagicMock, patch

import pytest


class TestCOMRetryMessageFilter:
    """Tests for the IMessageFilter implementation."""

    @pytest.fixture
    def filter_class(self):
        """Import the filter class."""
        from py_canoe.core.message_filter import COMRetryMessageFilter
        return COMRetryMessageFilter

    @pytest.fixture
    def mock_co_register(self):
        """Mock CoRegisterMessageFilter to avoid actual COM registration."""
        with patch("py_canoe.core.message_filter._CoRegisterMessageFilter") as mock:
            mock.return_value = 0  # S_OK
            yield mock

    def test_init_creates_vtable(self, filter_class, mock_co_register):
        """Filter creates a valid COM vtable structure."""
        f = filter_class()
        assert f._vtbl is not None
        assert f._impl is not None
        assert f._ptr is not None
        assert f._registered is False

    def test_register_calls_co_register_message_filter(self, filter_class, mock_co_register):
        """register() calls CoRegisterMessageFilter."""
        f = filter_class()
        f.register()
        assert mock_co_register.called
        assert f._registered is True

    def test_register_twice_is_noop(self, filter_class, mock_co_register):
        """Calling register() twice does not re-register."""
        f = filter_class()
        f.register()
        f.register()
        assert mock_co_register.call_count == 1

    def test_unregister_restores_old_filter(self, filter_class, mock_co_register):
        """unregister() restores the previous filter."""
        f = filter_class()
        f.register()
        f.unregister()
        assert mock_co_register.call_count == 2
        assert f._registered is False

    def test_unregister_without_register_is_noop(self, filter_class, mock_co_register):
        """unregister() without prior register() is safe."""
        f = filter_class()
        f.unregister()
        assert mock_co_register.call_count == 0

    def test_on_handle_incoming_returns_handled(self, filter_class, mock_co_register):
        """HandleInComingCall returns SERVERCALL_ISHANDLED (0)."""
        f = filter_class()
        result = f._on_handle_incoming(None, 0, None, 0, None)
        assert result == 0

    def test_on_message_pending_returns_waitnoprocess(self, filter_class, mock_co_register):
        """MessagePending returns PENDINGMSG_WAITNOPROCESS (1)."""
        f = filter_class()
        result = f._on_message_pending(None, None, 0, 0)
        assert result == 1

    def test_retry_rejected_backoff_under_1s(self, filter_class, mock_co_register):
        """RetryRejectedCall returns 100ms for first second."""
        f = filter_class()
        result = f._on_retry_rejected(None, None, 500, 1)  # 500ms, REJECTED
        assert result == 100

    def test_retry_rejected_backoff_1_to_5s(self, filter_class, mock_co_register):
        """RetryRejectedCall returns 500ms for 1-5 seconds."""
        f = filter_class()
        result = f._on_retry_rejected(None, None, 2000, 1)  # 2s
        assert result == 500

    def test_retry_rejected_backoff_5_to_30s(self, filter_class, mock_co_register):
        """RetryRejectedCall returns 2000ms for 5-30 seconds."""
        f = filter_class()
        result = f._on_retry_rejected(None, None, 10000, 1)  # 10s
        assert result == 2000

    def test_retry_rejected_backoff_30_to_60s(self, filter_class, mock_co_register):
        """RetryRejectedCall returns 5000ms for 30-60 seconds."""
        f = filter_class()
        result = f._on_retry_rejected(None, None, 45000, 1)  # 45s
        assert result == 5000

    def test_retry_rejected_gives_up_after_60s(self, filter_class, mock_co_register):
        """RetryRejectedCall returns CANCEL_CALL after 60 seconds."""
        f = filter_class()
        result = f._on_retry_rejected(None, None, 61000, 1)  # 61s
        assert result == 0xFFFFFFFF  # _CANCEL_CALL

    def test_retry_rejected_cancels_for_unknown_reject_type(self, filter_class, mock_co_register):
        """RetryRejectedCall cancels for unknown reject types."""
        f = filter_class()
        result = f._on_retry_rejected(None, None, 100, 99)  # unknown type
        assert result == 0xFFFFFFFF

    def test_retry_rejected_accepts_retrylater(self, filter_class, mock_co_register):
        """RetryRejectedCall retries for SERVERCALL_RETRYLATER (2)."""
        f = filter_class()
        result = f._on_retry_rejected(None, None, 100, 2)  # RETRYLATER
        assert result == 100

    def test_rejection_count_increments(self, filter_class, mock_co_register):
        """Each retry increments the rejection counter."""
        f = filter_class()
        assert f._rejection_count == 0
        f._on_retry_rejected(None, None, 0, 1)
        assert f._rejection_count == 1
        f._on_retry_rejected(None, None, 100, 1)
        assert f._rejection_count == 2


class TestApplicationMessageFilterIntegration:
    """Tests that Application registers the message filter."""

    @pytest.fixture
    def mock_dependencies(self):
        """Mock all COM dependencies."""
        with patch("py_canoe.core.application.win32com.client") as mock_win32:
            with patch("py_canoe.core.application.pythoncom"):
                with patch("py_canoe.core.message_filter._CoRegisterMessageFilter") as mock_reg:
                    mock_reg.return_value = 0
                    yield {"win32com": mock_win32, "co_register": mock_reg}

    def test_application_init_registers_filter(self, mock_dependencies):
        """Application.__init__ registers the IMessageFilter."""
        from py_canoe.core.application import Application
        app = Application(enable_events=False)
        assert app._message_filter is not None
        assert app._message_filter._registered is True
        assert mock_dependencies["co_register"].called
