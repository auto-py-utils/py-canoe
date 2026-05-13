from enum import Enum
import win32com.client

from py_canoe.core.child_elements.test_configuration_report import TestConfigurationReport
from py_canoe.core.child_elements.test_configuration_settings import TestConfigurationSettings
from py_canoe.core.child_elements.test_tree_elements import TestTreeElements
from py_canoe.core.child_elements.test_units import TestUnits
from py_canoe.core.child_elements.tcp_ip_stack_setting import TcpIpStackSetting
from py_canoe.helpers.common import logger, wait, DoEventsUntil

TEST_CONFIGURATION_TIMEOUT = 10  # seconds


class TestConfigurationVerdict(Enum):
    NOT_AVAILABLE = 0
    PASSED = 1
    FAILED = 2
    NONE = 3
    INCONCLUSIVE = 4
    ERROR_IN_TEST_SYSTEM = 5


class TestConfigurationStopReason(Enum):
    END = 0
    USER_ABORT = 1
    GENERAL_ERROR = 2
    VERDICT_IMPACT = 3
    TEST_CASE_INCONCLUSIVE = 4
    TEST_CASE_ERROR = 5


class TestConfigurationEvents:
    """The TestConfigurationEvents object provides access to events related to a test configuration."""
    def __init__(self):
        self.STARTED: bool = False
        self.STOPPED: bool = False
        self.STOP_REASON: TestConfigurationStopReason = TestConfigurationStopReason.END
        self.VERDICT: TestConfigurationVerdict = TestConfigurationVerdict.NOT_AVAILABLE

    def OnStart(self):
        self.STARTED = True

    def OnStop(self, reason: int):
        self.STOP_REASON = TestConfigurationStopReason(reason)
        self.STOPPED = True

    def OnVerdictChanged(self, verdict: int):
        self.VERDICT = TestConfigurationVerdict(verdict)

    def OnVerdictFail(self):
        pass


class TestConfiguration:
    """The TestConfiguration object represents a single test configuration within the CANoe configuration."""
    def __init__(self, com_object):
        self.com_object = win32com.client.Dispatch(com_object)
        self.test_configuration_events: TestConfigurationEvents = win32com.client.WithEvents(self.com_object, TestConfigurationEvents)

    @property
    def caption(self) -> str:
        return self.com_object.Caption

    @property
    def elements(self) -> 'TestTreeElements':
        return TestTreeElements(self.com_object.Elements)

    @property
    def enabled(self) -> bool:
        return self.com_object.Enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self.com_object.Enabled = value

    @property
    def id(self) -> str:
        return self.com_object.ID

    @property
    def name(self) -> str:
        return self.com_object.Name

    @property
    def report(self) -> 'TestConfigurationReport':
        return TestConfigurationReport(self.com_object.Report)

    @property
    def running(self) -> bool:
        return self.com_object.Running

    @property
    def settings(self) -> 'TestConfigurationSettings':
        return TestConfigurationSettings(self.com_object.Settings)

    @property
    def tcp_ip_stack_setting(self) -> 'TcpIpStackSetting':
        return TcpIpStackSetting(self.com_object.TcpIpStackSetting)

    @property
    def test_units(self) -> 'TestUnits':
        return TestUnits(self.com_object.TestUnits)

    @property
    def type(self) -> int:
        return self.com_object.Type

    @property
    def verdict(self) -> 'TestConfigurationVerdict':
        return TestConfigurationVerdict(self.com_object.Verdict)

    def apply_variants(self) -> None:
        self.com_object.ApplyVariants()

    def apply_variants_async(self) -> None:
        self.com_object.ApplyVariantsAsync()

    def contains_id(self, test_case_id: int) -> bool:
        return self.com_object.ContainsId(test_case_id)

    def pause(self) -> None:
        self.com_object.Pause()

    def resume(self) -> None:
        self.com_object.Resume()

    def start(self) -> None:
        self.test_configuration_events.STARTED = False
        self.com_object.Start()
        status = DoEventsUntil(lambda: self.test_configuration_events.STARTED, TEST_CONFIGURATION_TIMEOUT, "Test Configuration Start")
        if status:
            logger.info(f'started executing test configuration ({self.name})...')

    def stop(self) -> None:
        self.test_configuration_events.STOPPED = False
        self.com_object.Stop()
        status = DoEventsUntil(lambda: self.test_configuration_events.STOPPED, TEST_CONFIGURATION_TIMEOUT, "Test Configuration Stop")
        if status:
            logger.info(f'stopped test configuration ({self.name}) with stop reason {self.test_configuration_events.STOP_REASON.name} and verdict {self.test_configuration_events.VERDICT.name}')
