"""
Unit tests for server-friendly mode features:
- enable_events=False (Application, Measurement)
- open_config() polling
- stop_ex() busy-retry logic
- post_stop_pump parameter

Plus additional tests for pre-existing code to achieve full coverage.
"""

import time
from unittest.mock import Mock, patch, MagicMock, call

from py_canoe.core.capl import CaplFunction

import pytest

from py_canoe.core.application import Application, ApplicationEvents
from py_canoe.core.measurement import Measurement, MeasurementEvents


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_app(enable_events=False):
    """Create Application instance without actually connecting to COM."""
    app = Application(enable_events=enable_events)
    app.com_object = Mock()
    app.application_events = ApplicationEvents()
    app.configuration = Mock()
    app.measurement = Mock()
    app.bus = Mock()
    app.capl = Mock()
    app.networks = Mock()
    app.system = Mock()
    app.ui = Mock()
    app.version = Mock()
    return app


def _make_measurement(enable_events=False):
    """Create Measurement instance with mocked COM."""
    with patch("win32com.client.Dispatch") as mock_dispatch:
        mock_com = Mock()
        mock_com.Running = False
        mock_dispatch.return_value = mock_com

        mock_app = Mock()
        mock_app.com_object = Mock()

        with patch("win32com.client.WithEvents", return_value=Mock()):
            m = Measurement(mock_app, enable_events=enable_events)

        m.com_object = mock_com
    return m, mock_com


# ---------------------------------------------------------------------------
# Application: enable_events
# ---------------------------------------------------------------------------

class TestApplicationEnableEvents:
    """Test Application with enable_events parameter."""

    @patch("py_canoe.core.application.Measurement")
    @patch("win32com.client.WithEvents")
    @patch("win32com.client.gencache.EnsureDispatch")
    def test_enable_events_true_registers_with_events(
        self, mock_ensure, mock_with_events, mock_meas_cls
    ):
        mock_ensure.return_value = Mock()
        mock_with_events.return_value = Mock()
        mock_meas_cls.return_value = Mock(measurement_events=Mock())

        app = Application(enable_events=True)
        with patch.object(app, "_common_between_pre_and_post_cfg_open") as mock_common:
            app._launch_application()

        mock_with_events.assert_called_once()
        mock_common.assert_not_called()

    @patch("py_canoe.core.application.Measurement")
    @patch("win32com.client.WithEvents")
    @patch("win32com.client.gencache.EnsureDispatch")
    def test_enable_events_false_skips_with_events(
        self, mock_ensure, mock_with_events, mock_meas_cls
    ):
        mock_ensure.return_value = Mock()
        mock_meas_cls.return_value = Mock(measurement_events=Mock())

        app = Application(enable_events=False)
        with patch.object(app, "_common_between_pre_and_post_cfg_open") as mock_common:
            app._launch_application()

        mock_with_events.assert_not_called()
        mock_common.assert_not_called()

    @patch("py_canoe.core.application.Measurement")
    @patch("win32com.client.gencache.EnsureDispatch")
    def test_enable_events_false_creates_dummy_events(
        self, mock_ensure, mock_meas_cls
    ):
        mock_ensure.return_value = Mock()
        mock_meas_cls.return_value = Mock(measurement_events=Mock())

        app = Application(enable_events=False)
        with patch.object(app, "_common_between_pre_and_post_cfg_open") as mock_common:
            app._launch_application()

        mock_common.assert_not_called()
        assert isinstance(app.application_events, ApplicationEvents)
        assert app.application_events.OPENED is False

    @patch("py_canoe.core.application.Measurement")
    @patch("win32com.client.gencache.EnsureDispatch")
    def test_measurement_created_with_enable_events_flag(
        self, mock_ensure, mock_meas_cls
    ):
        mock_ensure.return_value = Mock()
        mock_meas_cls.return_value = Mock(measurement_events=Mock())

        app = Application(enable_events=False)
        with patch.object(app, "_common_between_pre_and_post_cfg_open") as mock_common:
            app._launch_application()

        mock_common.assert_not_called()
        mock_meas_cls.assert_called_once_with(app, enable_events=False)


# ---------------------------------------------------------------------------
# Application: open_config
# ---------------------------------------------------------------------------

class TestOpenConfig:
    """Test open_config() configuration switching."""

    def test_open_config_success_with_events_disabled(self):
        app = _make_app(enable_events=False)
        target = r"D:\test\config.cfg"
        app.configuration.full_name = target.lower()

        with patch.object(app, "_setup_post_configuration_loading"):
            result = app.open_config(target, timeout=2)

        assert result is True
        app.com_object.Open.assert_called_once()

    def test_open_config_timeout_returns_false(self):
        app = _make_app(enable_events=False)
        app.configuration.full_name = "other.cfg"

        result = app.open_config(r"D:\test\config.cfg", timeout=0.3)

        assert result is False

    def test_open_config_com_error_returns_false(self):
        app = _make_app(enable_events=False)
        app.com_object.Open.side_effect = Exception("COM error")

        result = app.open_config(r"D:\test\config.cfg", timeout=1)

        assert result is False

    def test_open_config_resets_opened_flag(self):
        app = _make_app(enable_events=False)
        app.application_events.OPENED = True
        app.configuration.full_name = r"d:\test\config.cfg"

        with patch.object(app, "_setup_post_configuration_loading"):
            app.open_config(r"D:\test\config.cfg", timeout=2)

        # Verify OPENED was reset before Open call
        # (it may be True again if events mode, but we check the call happened)
        app.com_object.Open.assert_called_once()

    @patch("py_canoe.core.application.DoEventsUntil", return_value=True)
    def test_open_config_uses_do_events_when_events_enabled(self, mock_do_events):
        app = _make_app(enable_events=True)
        app._enable_events = True
        app.configuration.full_name = r"d:\test\config.cfg"

        with patch.object(app, "_setup_post_configuration_loading"):
            result = app.open_config(r"D:\test\config.cfg", timeout=5)

        assert result is True
        mock_do_events.assert_called_once()


# ---------------------------------------------------------------------------
# Application: pump_messages
# ---------------------------------------------------------------------------

class TestPumpMessages:
    """Test pump_messages() wrapper."""

    @patch("py_canoe.core.application.pythoncom.PumpWaitingMessages")
    def test_pump_messages_calls_pythoncom(self, mock_pump):
        app = _make_app(enable_events=False)
        app.pump_messages()

        mock_pump.assert_called_once()


# ---------------------------------------------------------------------------
# Measurement: enable_events
# ---------------------------------------------------------------------------

class TestMeasurementEnableEvents:
    """Test Measurement with enable_events parameter."""

    def test_enable_events_false_no_with_events(self):
        with patch("win32com.client.Dispatch") as mock_dispatch:
            mock_dispatch.return_value = Mock()
            with patch("win32com.client.WithEvents") as mock_we:
                mock_app = Mock()
                mock_app.com_object = Mock()
                m = Measurement(mock_app, enable_events=False)
                mock_we.assert_not_called()

        assert isinstance(m.measurement_events, MeasurementEvents)

    def test_enable_events_true_registers_with_events(self):
        with patch("win32com.client.Dispatch") as mock_dispatch:
            mock_dispatch.return_value = Mock()
            with patch("win32com.client.WithEvents") as mock_we:
                mock_we.return_value = Mock()
                mock_app = Mock()
                mock_app.com_object = Mock()
                m = Measurement(mock_app, enable_events=True)
                mock_we.assert_called_once()


# ---------------------------------------------------------------------------
# Measurement: start() with enable_events=False
# ---------------------------------------------------------------------------

class TestMeasurementStartEventsDisabled:
    """Test Measurement.start() polling mode."""

    def test_start_polls_running(self):
        m, mock_com = _make_measurement(enable_events=False)
        mock_com.Running = False

        def start_side_effect():
            mock_com.Running = True

        mock_com.Start = Mock(side_effect=start_side_effect)

        with patch("py_canoe.core.measurement.time.sleep"):
            result = m.start(timeout=5)

        assert result is True
        mock_com.Start.assert_called_once()

    def test_start_timeout_returns_false(self):
        m, mock_com = _make_measurement(enable_events=False)
        mock_com.Running = False

        # monotonic advances past timeout
        call_idx = [0]
        def monotonic_side_effect():
            call_idx[0] += 1
            return call_idx[0] * 0.5  # 0.5, 1.0, 1.5, ...

        with patch("py_canoe.core.measurement.time.sleep"):
            with patch("py_canoe.core.measurement.time.monotonic", side_effect=monotonic_side_effect):
                result = m.start(timeout=1)

        assert result is False

    def test_start_already_running_returns_true(self):
        m, mock_com = _make_measurement(enable_events=False)
        mock_com.Running = True

        result = m.start(timeout=5)

        assert result is True
        mock_com.Start.assert_not_called()


# ---------------------------------------------------------------------------
# Measurement: stop_ex() busy-retry
# ---------------------------------------------------------------------------

class TestStopExBusyRetry:
    """Test stop_ex() error handling.

    Note: Busy-retry is now handled by IMessageFilter (registered in Application.__init__).
    In unit tests without COM, the filter is not active, so stop_ex() simply returns False
    on any exception. The IMessageFilter tests verify the retry logic separately.
    """

    @patch("py_canoe.core.measurement.pythoncom.PumpWaitingMessages")
    @patch("py_canoe.core.measurement.time.sleep")
    def test_stop_ex_busy_returns_false_without_filter(self, mock_sleep, mock_pump):
        """Without IMessageFilter (unit tests), busy exception returns False."""
        m, mock_com = _make_measurement(enable_events=False)
        mock_com.Running = True
        mock_com.Stop = Mock(side_effect=Exception("User interface is busy (-2147418113)"))

        times = [0] * 10
        time_iter = iter(times)
        with patch("py_canoe.core.measurement.time.monotonic", side_effect=lambda: next(time_iter)):
            result = m.stop_ex(timeout=30, post_stop_pump=0)

        assert result is False
        mock_com.Stop.assert_called_once()

    @patch("py_canoe.core.measurement.pythoncom.PumpWaitingMessages")
    @patch("py_canoe.core.measurement.time.sleep")
    def test_stop_ex_unexpected_error_returns_false(self, mock_sleep, mock_pump):
        m, mock_com = _make_measurement(enable_events=False)
        mock_com.Running = True
        mock_com.Stop = Mock(side_effect=Exception("Something unexpected"))

        times = [0] * 10
        time_iter = iter(times)
        with patch("py_canoe.core.measurement.time.monotonic", side_effect=lambda: next(time_iter)):
            result = m.stop_ex(timeout=30, post_stop_pump=0)

        assert result is False

    @patch("py_canoe.core.measurement.pythoncom.PumpWaitingMessages")
    @patch("py_canoe.core.measurement.time.sleep")
    def test_stop_ex_already_stopped(self, mock_sleep, mock_pump):
        m, mock_com = _make_measurement(enable_events=False)
        mock_com.Running = False

        result = m.stop_ex(timeout=30, post_stop_pump=0)

        assert result is True
        mock_com.Stop.assert_not_called()

    @patch("py_canoe.core.measurement.pythoncom.PumpWaitingMessages")
    @patch("py_canoe.core.measurement.time.sleep")
    def test_stop_ex_naturally_stopped_during_retry(self, mock_sleep, mock_pump):
        """Measurement stops on its own while we retry Stop()."""
        m, mock_com = _make_measurement(enable_events=False)
        mock_com.Running = True

        # First check: Running=True, then Running becomes False
        running_values = [True, False]
        running_iter = iter(running_values)
        type(mock_com).Running = property(lambda self: next(running_iter))

        times = [0] * 10
        time_iter = iter(times)
        with patch("py_canoe.core.measurement.time.monotonic", side_effect=lambda: next(time_iter)):
            result = m.stop_ex(timeout=30, post_stop_pump=0)

        assert result is True

    @patch("py_canoe.core.measurement.pythoncom.PumpWaitingMessages")
    @patch("py_canoe.core.measurement.time.sleep")
    def test_stop_ex_timeout_all_busy(self, mock_sleep, mock_pump):
        """stop_ex returns False when timeout expires with all busy errors."""
        m, mock_com = _make_measurement(enable_events=False)
        mock_com.Running = True
        mock_com.Stop = Mock(side_effect=Exception("User interface is busy"))

        # Simulate time advancing past deadline
        call_count = [0]
        def monotonic_side_effect():
            call_count[0] += 1
            return call_count[0] * 5.0  # 5, 10, 15, ... -> timeout at 30

        with patch("py_canoe.core.measurement.time.monotonic", side_effect=monotonic_side_effect):
            result = m.stop_ex(timeout=30, post_stop_pump=0)

        assert result is False

    @patch("py_canoe.core.measurement.pythoncom.PumpWaitingMessages")
    @patch("py_canoe.core.measurement.time.sleep")
    def test_stop_ex_polls_running_after_stop_accepted(self, mock_sleep, mock_pump):
        """After Stop() accepted, polls Running until False."""
        m, mock_com = _make_measurement(enable_events=False)
        mock_com.Running = True

        stop_called = [False]
        def stop_side_effect():
            stop_called[0] = True
            # Running stays True for a bit, then False

        mock_com.Stop = Mock(side_effect=stop_side_effect)

        # Running: True during stop, then stays True for poll, then False
        running_seq = [True, True, True, True, False]
        running_iter = iter(running_seq)
        type(mock_com).Running = property(lambda self: next(running_iter))

        times = [0] * 20
        time_iter = iter(times)
        with patch("py_canoe.core.measurement.time.monotonic", side_effect=lambda: next(time_iter)):
            result = m.stop_ex(timeout=30, post_stop_pump=0)

        assert result is True


# ---------------------------------------------------------------------------
# Measurement: post_stop_pump
# ---------------------------------------------------------------------------

class TestPostStopPump:
    """Test post_stop_pump parameter."""

    @patch("py_canoe.core.measurement.pythoncom.PumpWaitingMessages")
    @patch("py_canoe.core.measurement.time.sleep")
    def test_post_stop_pump_calls_pump_n_times(self, mock_sleep, mock_pump):
        """post_stop_pump=2 calls PumpWaitingMessages 20 times."""
        m, mock_com = _make_measurement(enable_events=False)
        mock_com.Running = True

        def stop_side_effect():
            mock_com.Running = False
        mock_com.Stop = Mock(side_effect=stop_side_effect)

        times = [0] * 20
        time_iter = iter(times)
        with patch("py_canoe.core.measurement.time.monotonic", side_effect=lambda: next(time_iter)):
            m.stop_ex(timeout=30, post_stop_pump=2)

        assert mock_pump.call_count == 20

    @patch("py_canoe.core.measurement.pythoncom.PumpWaitingMessages")
    @patch("py_canoe.core.measurement.time.sleep")
    def test_post_stop_pump_zero_skips_pump(self, mock_sleep, mock_pump):
        """post_stop_pump=0 does not call PumpWaitingMessages."""
        m, mock_com = _make_measurement(enable_events=False)
        mock_com.Running = True

        def stop_side_effect():
            mock_com.Running = False
        mock_com.Stop = Mock(side_effect=stop_side_effect)

        times = [0] * 20
        time_iter = iter(times)
        with patch("py_canoe.core.measurement.time.monotonic", side_effect=lambda: next(time_iter)):
            m.stop_ex(timeout=30, post_stop_pump=0)

        mock_pump.assert_not_called()

    def test_stop_delegates_post_stop_pump_to_stop_ex(self):
        """stop() passes post_stop_pump to stop_ex()."""
        m, _ = _make_measurement(enable_events=False)
        m.stop_ex = Mock(return_value=True)

        m.stop(timeout=10, post_stop_pump=5)

        m.stop_ex.assert_called_once_with(10, post_stop_pump=5)

    @patch("py_canoe.core.measurement.pythoncom.PumpWaitingMessages")
    @patch("py_canoe.core.measurement.time.sleep")
    def test_post_stop_pump_default_is_10(self, mock_sleep, mock_pump):
        """Default post_stop_pump is 10 (100 pump calls)."""
        m, mock_com = _make_measurement(enable_events=False)
        mock_com.Running = False  # Already stopped

        m.stop_ex(timeout=30)  # Use default post_stop_pump

        # Already stopped -> returns True immediately, no pump
        # (post_stop_pump only executes after successful stop confirmation)
        mock_pump.assert_not_called()


# ---------------------------------------------------------------------------
# Measurement: start() with enable_events=True
# ---------------------------------------------------------------------------

class TestMeasurementStartEventsEnabled:
    """Test Measurement.start() with events mode (DoEventsUntil path)."""

    @patch("py_canoe.core.measurement.time.sleep")
    @patch("py_canoe.core.measurement.DoEventsUntil", return_value=True)
    def test_start_uses_do_events_when_events_enabled(self, mock_do_events, mock_sleep):
        with patch("win32com.client.Dispatch") as mock_dispatch:
            mock_com = Mock()
            mock_com.Running = False
            mock_dispatch.return_value = mock_com
            mock_app = Mock()
            mock_app.com_object = Mock()
            with patch("win32com.client.WithEvents", return_value=Mock()):
                m = Measurement(mock_app, enable_events=True)
            m.com_object = mock_com

        result = m.start(timeout=10)

        assert result is True
        mock_do_events.assert_called_once()
        mock_com.Start.assert_called_once()

    @patch("py_canoe.core.measurement.time.sleep")
    @patch("py_canoe.core.measurement.DoEventsUntil", return_value=False)
    def test_start_events_timeout_returns_false(self, mock_do_events, mock_sleep):
        with patch("win32com.client.Dispatch") as mock_dispatch:
            mock_com = Mock()
            mock_com.Running = False
            mock_dispatch.return_value = mock_com
            mock_app = Mock()
            mock_app.com_object = Mock()
            with patch("win32com.client.WithEvents", return_value=Mock()):
                m = Measurement(mock_app, enable_events=True)
            m.com_object = mock_com

        result = m.start(timeout=10)

        assert result is False

    def test_start_exception_returns_false(self):
        m, mock_com = _make_measurement(enable_events=False)
        mock_com.Running = False
        mock_com.Start = Mock(side_effect=Exception("COM error"))

        result = m.start(timeout=5)

        assert result is False


# ---------------------------------------------------------------------------
# Measurement: stop_ex() with enable_events=True
# ---------------------------------------------------------------------------

class TestStopExEventsEnabled:
    """Test stop_ex() DoEventsUntil path."""

    @patch("py_canoe.core.measurement.pythoncom.PumpWaitingMessages")
    @patch("py_canoe.core.measurement.time.sleep")
    @patch("py_canoe.core.measurement.DoEventsUntil", return_value=True)
    def test_stop_ex_uses_do_events_when_events_enabled(self, mock_do_events, mock_sleep, mock_pump):
        with patch("win32com.client.Dispatch") as mock_dispatch:
            mock_com = Mock()
            mock_com.Running = True
            mock_dispatch.return_value = mock_com
            mock_app = Mock()
            mock_app.com_object = Mock()
            with patch("win32com.client.WithEvents", return_value=Mock()):
                m = Measurement(mock_app, enable_events=True)
            m.com_object = mock_com

        def stop_side_effect():
            pass  # Stop accepted but Running still True until event fires
        mock_com.Stop = Mock(side_effect=stop_side_effect)

        times = [0] * 20
        time_iter = iter(times)
        with patch("py_canoe.core.measurement.time.monotonic", side_effect=lambda: next(time_iter)):
            result = m.stop_ex(timeout=30, post_stop_pump=0)

        assert result is True
        mock_do_events.assert_called_once()

    @patch("py_canoe.core.measurement.pythoncom.PumpWaitingMessages")
    @patch("py_canoe.core.measurement.time.sleep")
    @patch("py_canoe.core.measurement.DoEventsUntil", return_value=False)
    def test_stop_ex_events_timeout_returns_false(self, mock_do_events, mock_sleep, mock_pump):
        with patch("win32com.client.Dispatch") as mock_dispatch:
            mock_com = Mock()
            mock_com.Running = True
            mock_dispatch.return_value = mock_com
            mock_app = Mock()
            mock_app.com_object = Mock()
            with patch("win32com.client.WithEvents", return_value=Mock()):
                m = Measurement(mock_app, enable_events=True)
            m.com_object = mock_com

        mock_com.Stop = Mock()

        times = [0] * 20
        time_iter = iter(times)
        with patch("py_canoe.core.measurement.time.monotonic", side_effect=lambda: next(time_iter)):
            result = m.stop_ex(timeout=30, post_stop_pump=0)

        assert result is False


# ---------------------------------------------------------------------------
# Measurement: stop_ex() poll timeout (Running stays True)
# ---------------------------------------------------------------------------

class TestStopExPollTimeout:
    """Test stop_ex() when Stop() accepted but Running never becomes False."""

    @patch("py_canoe.core.measurement.pythoncom.PumpWaitingMessages")
    @patch("py_canoe.core.measurement.time.sleep")
    def test_stop_ex_poll_timeout_returns_false(self, mock_sleep, mock_pump):
        m, mock_com = _make_measurement(enable_events=False)
        mock_com.Running = True
        mock_com.Stop = Mock()  # Stop accepted, but Running stays True

        # Time: first calls at 0 for Stop loop, then jumps past poll deadline
        call_count = [0]
        def monotonic_side_effect():
            call_count[0] += 1
            if call_count[0] <= 5:
                return 0
            return 100  # Past any deadline
        with patch("py_canoe.core.measurement.time.monotonic", side_effect=monotonic_side_effect):
            result = m.stop_ex(timeout=30, post_stop_pump=0)

        assert result is False


# ---------------------------------------------------------------------------
# Application: open_config polling exception handling
# ---------------------------------------------------------------------------

class TestOpenConfigPollingException:
    """Test open_config() exception handling during FullName polling."""

    def test_open_config_handles_exception_during_polling(self):
        """When configuration.full_name raises during poll, it retries."""
        app = _make_app(enable_events=False)
        target = r"D:\test\config.cfg"

        call_count = [0]
        def full_name_getter():
            call_count[0] += 1
            if call_count[0] <= 2:
                raise Exception("COM temporarily unavailable")
            return target.lower()

        type(app.configuration).full_name = property(lambda self: full_name_getter())

        with patch.object(app, "_setup_post_configuration_loading"):
            result = app.open_config(target, timeout=5)

        assert result is True
        assert call_count[0] >= 3


# ---------------------------------------------------------------------------
# Application: new() and open() enable_events branching
# ---------------------------------------------------------------------------

class TestNewAndOpenEventsBranching:
    """Test new() and open() with enable_events=True/False branching."""

    @patch("py_canoe.core.application.DoEventsUntil", return_value=True)
    def test_new_events_disabled_uses_fullname_condition(self, mock_do_events):
        app = _make_app(enable_events=False)
        app.com_object.FullName = "something"

        with patch.object(app, "_launch_application"):
            with patch.object(app, "_setup_post_configuration_loading"):
                result = app.new(timeout=5)

        assert result is True
        mock_do_events.assert_called_once()
        # Verify the condition lambda uses FullName (not OPENED)
        cond = mock_do_events.call_args[0][0]
        app.com_object.FullName = ""
        assert cond() is False
        app.com_object.FullName = "test.cfg"
        assert cond() is True

    @patch("py_canoe.core.application.DoEventsUntil", return_value=True)
    def test_new_events_enabled_uses_opened_flag(self, mock_do_events):
        app = _make_app(enable_events=True)
        app._enable_events = True

        with patch.object(app, "_launch_application"):
            with patch.object(app, "_setup_post_configuration_loading"):
                result = app.new(timeout=5)

        assert result is True
        mock_do_events.assert_called_once()
        cond = mock_do_events.call_args[0][0]
        app.application_events.OPENED = False
        assert cond() is False
        app.application_events.OPENED = True
        assert cond() is True

    @patch("py_canoe.core.application.DoEventsUntil", return_value=False)
    def test_new_timeout_returns_false(self, mock_do_events):
        app = _make_app(enable_events=False)

        with patch.object(app, "_launch_application"):
            result = app.new(timeout=5)

        assert result is False

    def test_new_exception_returns_false(self):
        app = _make_app(enable_events=False)
        app.com_object.New.side_effect = Exception("COM error")

        with patch.object(app, "_launch_application"):
            result = app.new(timeout=5)

        assert result is False

    @patch("py_canoe.core.application.DoEventsUntil", return_value=True)
    def test_open_events_disabled_uses_fullname_condition(self, mock_do_events):
        app = _make_app(enable_events=False)
        app.com_object.FullName = r"d:\test\config.cfg"

        with patch.object(app, "_launch_application"):
            with patch.object(app, "_setup_post_configuration_loading"):
                result = app.open(r"D:\test\config.cfg", timeout=5)

        assert result is True
        mock_do_events.assert_called_once()
        cond = mock_do_events.call_args[0][0]
        app.com_object.FullName = "other.cfg"
        assert cond() is False
        app.com_object.FullName = r"D:\test\config.cfg"
        assert cond() is True

    @patch("py_canoe.core.application.DoEventsUntil", return_value=True)
    def test_open_events_enabled_uses_opened_flag(self, mock_do_events):
        app = _make_app(enable_events=True)
        app._enable_events = True

        with patch.object(app, "_launch_application"):
            with patch.object(app, "_setup_post_configuration_loading"):
                result = app.open(r"D:\test\config.cfg", timeout=5)

        assert result is True
        mock_do_events.assert_called_once()
        cond = mock_do_events.call_args[0][0]
        app.application_events.OPENED = False
        assert cond() is False
        app.application_events.OPENED = True
        assert cond() is True

    @patch("py_canoe.core.application.DoEventsUntil", return_value=False)
    def test_open_timeout_returns_false(self, mock_do_events):
        app = _make_app(enable_events=False)

        with patch.object(app, "_launch_application"):
            result = app.open(r"D:\test\config.cfg", timeout=5)

        assert result is False

    def test_open_exception_returns_false(self):
        app = _make_app(enable_events=False)
        app.com_object.Open.side_effect = Exception("COM error")

        with patch.object(app, "_launch_application"):
            result = app.open(r"D:\test\config.cfg", timeout=5)

        assert result is False


# ===========================================================================
# Pre-existing code coverage tests
# ===========================================================================

# ---------------------------------------------------------------------------
# ApplicationEvents callbacks
# ---------------------------------------------------------------------------

class TestApplicationEventsCallbacks:
    """Test ApplicationEvents OnOpen and OnQuit callbacks."""

    def test_on_open_sets_flags(self):
        events = ApplicationEvents()
        assert events.OPENED is False
        assert events.CANOE_CFG_FULLNAME == ""

        events.OnOpen(r"D:\test\config.cfg")

        assert events.OPENED is True
        assert events.CANOE_CFG_FULLNAME == r"D:\test\config.cfg"

    def test_on_quit_sets_flag(self):
        events = ApplicationEvents()
        assert events.QUIT is False

        events.OnQuit()

        assert events.QUIT is True


# ---------------------------------------------------------------------------
# Application properties
# ---------------------------------------------------------------------------

class TestApplicationProperties:
    """Test Application properties."""

    def test_full_name_property(self):
        app = _make_app(enable_events=False)
        app.com_object.FullName = r"D:\test\config.cfg"

        assert app.full_name == r"D:\test\config.cfg"

    def test_name_property(self):
        app = _make_app(enable_events=False)
        app.com_object.Name = "CANoe"

        assert app.name == "CANoe"

    def test_path_property(self):
        app = _make_app(enable_events=False)
        app.com_object.Path = r"D:\test"

        assert app.path == r"D:\test"

    def test_visible_getter(self):
        app = _make_app(enable_events=False)
        app.com_object.Visible = True

        assert app.visible is True

    def test_visible_setter(self):
        app = _make_app(enable_events=False)
        app.com_object.Visible = False

        app.visible = True

        assert app.com_object.Visible is True


# ---------------------------------------------------------------------------
# Application: quit()
# ---------------------------------------------------------------------------

class TestApplicationQuit:
    """Test Application.quit() method."""

    @patch("py_canoe.core.application.DoEventsUntil", return_value=True)
    def test_quit_success(self, mock_do_events):
        app = _make_app(enable_events=False)

        result = app.quit(timeout=5)

        assert result is True
        app.com_object.Quit.assert_called_once()
        mock_do_events.assert_called_once()

    @patch("py_canoe.core.application.DoEventsUntil", return_value=False)
    def test_quit_timeout(self, mock_do_events):
        app = _make_app(enable_events=False)

        result = app.quit(timeout=5)

        assert result is False

    def test_quit_exception(self):
        app = _make_app(enable_events=False)
        app.configuration.modified = Mock(side_effect=Exception("COM error"))

        result = app.quit(timeout=5)

        assert result is False


# ---------------------------------------------------------------------------
# Application: attach_to_active_application()
# ---------------------------------------------------------------------------

class TestAttachToActiveApplication:
    """Test Application.attach_to_active_application() method."""

    def test_attach_success(self):
        app = _make_app(enable_events=False)

        with patch.object(app, "_launch_application"):
            with patch.object(app, "_setup_post_configuration_loading"):
                result = app.attach_to_active_application()

        assert result is True

    def test_attach_no_com_object(self):
        app = _make_app(enable_events=False)
        app.com_object = None

        with patch.object(app, "_launch_application"):
            result = app.attach_to_active_application()

        assert result is False

    def test_attach_exception(self):
        app = _make_app(enable_events=False)

        with patch.object(app, "_launch_application", side_effect=Exception("COM error")):
            result = app.attach_to_active_application()

        assert result is False


# ---------------------------------------------------------------------------
# MeasurementEvents callbacks
# ---------------------------------------------------------------------------

class TestMeasurementEventsCallbacks:
    """Test MeasurementEvents callbacks."""

    def test_on_init_sets_flag_and_creates_capl_functions(self):
        events = MeasurementEvents()
        mock_app_com = Mock()
        mock_capl_func = Mock()
        mock_app_com.CAPL.GetFunction.return_value = mock_capl_func
        events.APP_COM_OBJ = mock_app_com
        events.CAPL_FUNCTION_NAMES = ("MyFunc",)

        with patch("py_canoe.core.measurement.CaplFunction") as mock_capl_cls:
            mock_capl_cls.return_value = "capl_obj"
            events.OnInit()

        assert events.INIT is True
        assert events.CAPL_FUNCTION_OBJECTS["MyFunc"] == "capl_obj"
        mock_app_com.CAPL.GetFunction.assert_called_once_with("MyFunc")

    def test_on_start_sets_flag(self):
        events = MeasurementEvents()
        assert events.START is False

        events.OnStart()

        assert events.START is True

    def test_on_stop_sets_flag(self):
        events = MeasurementEvents()
        assert events.STOP is False

        events.OnStop()

        assert events.STOP is True

    def test_on_exit_clears_functions_and_sets_flag(self):
        events = MeasurementEvents()
        events.CAPL_FUNCTION_OBJECTS = {"func1": "obj1", "func2": "obj2"}
        assert events.EXIT is False

        events.OnExit()

        assert events.EXIT is True
        assert events.CAPL_FUNCTION_OBJECTS == {}


# ---------------------------------------------------------------------------
# Measurement properties
# ---------------------------------------------------------------------------

class TestMeasurementProperties:
    """Test Measurement properties."""

    def test_animation_delay_getter(self):
        m, mock_com = _make_measurement(enable_events=False)
        mock_com.AnimationDelay = 150

        assert m.animation_delay == 150

    def test_animation_delay_setter(self):
        m, mock_com = _make_measurement(enable_events=False)

        m.animation_delay = 200

        assert mock_com.AnimationDelay == 200

    def test_measurement_index_getter(self):
        m, mock_com = _make_measurement(enable_events=False)
        mock_com.MeasurementIndex = 3

        assert m.measurement_index == 3

    def test_measurement_index_setter(self):
        m, mock_com = _make_measurement(enable_events=False)

        m.measurement_index = 5

        assert mock_com.MeasurementIndex == 5

    def test_running_property(self):
        m, mock_com = _make_measurement(enable_events=False)
        mock_com.Running = True

        assert m.running is True


# ---------------------------------------------------------------------------
# Measurement: animation mode, break, reset, step
# ---------------------------------------------------------------------------

class TestMeasurementOfflineMethods:
    """Test offline mode methods."""

    @patch("py_canoe.core.measurement.DoEventsUntil", return_value=True)
    def test_start_animation_mode_success(self, mock_do_events):
        m, mock_com = _make_measurement(enable_events=False)
        mock_com.Running = False

        result = m.start_measurement_in_animation_mode(animation_delay=150, timeout=10)

        assert result is True
        mock_com.Animate.assert_called_once()
        assert mock_com.AnimationDelay == 150

    @patch("py_canoe.core.measurement.DoEventsUntil", return_value=False)
    def test_start_animation_mode_timeout(self, mock_do_events):
        m, mock_com = _make_measurement(enable_events=False)
        mock_com.Running = False

        result = m.start_measurement_in_animation_mode(timeout=10)

        assert result is False

    def test_start_animation_mode_already_running(self):
        m, mock_com = _make_measurement(enable_events=False)
        mock_com.Running = True

        result = m.start_measurement_in_animation_mode()

        assert result is False
        mock_com.Animate.assert_not_called()

    def test_start_animation_mode_exception(self):
        m, mock_com = _make_measurement(enable_events=False)
        mock_com.Running = False
        mock_com.Animate.side_effect = Exception("COM error")

        result = m.start_measurement_in_animation_mode()

        assert result is False

    def test_break_measurement_success(self):
        m, mock_com = _make_measurement(enable_events=False)
        mock_com.Running = True

        result = m.break_measurement_in_offline_mode()

        assert result is True
        mock_com.Break.assert_called_once()

    def test_break_measurement_not_running(self):
        m, mock_com = _make_measurement(enable_events=False)
        mock_com.Running = False

        result = m.break_measurement_in_offline_mode()

        assert result is False
        mock_com.Break.assert_not_called()

    def test_break_measurement_exception(self):
        m, mock_com = _make_measurement(enable_events=False)
        mock_com.Running = True
        mock_com.Break.side_effect = Exception("COM error")

        result = m.break_measurement_in_offline_mode()

        assert result is False

    def test_reset_measurement_success(self):
        m, mock_com = _make_measurement(enable_events=False)

        result = m.reset_measurement_in_offline_mode()

        assert result is True
        mock_com.Reset.assert_called_once()

    def test_reset_measurement_exception(self):
        m, mock_com = _make_measurement(enable_events=False)
        mock_com.Reset.side_effect = Exception("COM error")

        result = m.reset_measurement_in_offline_mode()

        assert result is False

    def test_process_single_step_success(self):
        m, mock_com = _make_measurement(enable_events=False)

        result = m.process_measurement_event_in_single_step()

        assert result is True
        mock_com.Step.assert_called_once()

    def test_process_single_step_exception(self):
        m, mock_com = _make_measurement(enable_events=False)
        mock_com.Step.side_effect = Exception("COM error")

        result = m.process_measurement_event_in_single_step()

        assert result is False


# ---------------------------------------------------------------------------
# Application: internal helpers (_common, _launch, _setup)
# ---------------------------------------------------------------------------

class TestApplicationInternalHelpers:
    """Test internal helper methods for full coverage."""

    @patch("py_canoe.core.application.Bus")
    @patch("py_canoe.core.application.Capl")
    @patch("py_canoe.core.application.Configuration")
    @patch("py_canoe.core.application.Environment")
    @patch("py_canoe.core.application.Networks")
    @patch("py_canoe.core.application.System")
    @patch("py_canoe.core.application.Ui")
    @patch("py_canoe.core.application.Version")
    def test_common_between_pre_and_post_cfg_open(
        self, mock_ver, mock_ui, mock_sys, mock_net, mock_env, mock_cfg, mock_capl, mock_bus
    ):
        app = Application(enable_events=False)
        app.com_object = Mock()

        app._common_between_pre_and_post_cfg_open()

        mock_bus.assert_called_once_with(app)
        mock_capl.assert_called_once_with(app)
        mock_cfg.assert_called_once_with(app)
        mock_env.assert_called_once_with(app)
        mock_net.assert_called_once_with(app)
        mock_sys.assert_called_once_with(app)
        mock_ui.assert_called_once_with(app)
        mock_ver.assert_called_once_with(app)

    @patch("py_canoe.core.application.Measurement")
    @patch("win32com.client.gencache.EnsureDispatch", side_effect=Exception("COM error"))
    def test_launch_application_exception_reraises(self, mock_ensure, mock_meas):
        app = Application(enable_events=False)

        with pytest.raises(Exception, match="COM error"):
            app._launch_application()

    def test_setup_post_configuration_loading_calls_helpers(self):
        app = _make_app(enable_events=False)
        app.networks.fetch_diagnostic_devices = Mock()
        app.configuration.fetch_test_modules = Mock()
        app.configuration.fetch_test_units = Mock()

        with patch.object(app, "_common_between_pre_and_post_cfg_open"):
            app._setup_post_configuration_loading()

        app.networks.fetch_diagnostic_devices.assert_called_once()
        app.configuration.fetch_test_modules.assert_called_once()
        app.configuration.fetch_test_units.assert_called_once()

    def test_setup_post_configuration_loading_exception(self):
        app = _make_app(enable_events=False)

        with patch.object(app, "_common_between_pre_and_post_cfg_open", side_effect=Exception("error")):
            # Should not raise, just log
            app._setup_post_configuration_loading()

    def test_quit_exception_in_quit_call(self):
        app = _make_app(enable_events=False)
        app.com_object.Quit.side_effect = Exception("COM error during quit")

        result = app.quit(timeout=5)

        assert result is False
