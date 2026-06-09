import win32com.client

from py_canoe.helpers.common import DoEventsUntil


class TestConfigurationReportEvents:
    """Event handlers for TestConfiguration COM object events."""
    def __init__(self):
        self.SUCCESS = False
        self.SOURCE_FULL_NAME = ""
        self.GENERATED_FULL_NAME = ""

    def OnGenerated(self, success: bool, source_full_name: str, generated_full_name: str):
        self.SUCCESS = success
        self.SOURCE_FULL_NAME = source_full_name
        self.GENERATED_FULL_NAME = generated_full_name


class TestConfigurationReport:
    """The TestConfigurationReport object represents the reporting settings of a test configuration."""
    def __init__(self, com_object):
        self.com_object = win32com.client.Dispatch(com_object)
        self.test_configuration_report_events: TestConfigurationReportEvents = win32com.client.WithEvents(self.com_object, TestConfigurationReportEvents)

    @property
    def filter_settings(self) -> 'TestConfigurationReport':
        return self.com_object.FilterSettings

    @property
    def full_path(self) -> str:
        return self.com_object.FullPath

    @full_path.setter
    def full_path(self, value: str):
        self.com_object.FullPath = value

    @property
    def last_written_full_path(self) -> str:
        return self.com_object.LastWrittenFullPath

    @property
    def style_sheet(self) -> str:
        return self.com_object.StyleSheet

    @style_sheet.setter
    def style_sheet(self, value: str):
        self.com_object.StyleSheet = value

    @property
    def style_sheet_enabled(self) -> bool:
        return self.com_object.StyleSheetEnabled

    @style_sheet_enabled.setter
    def style_sheet_enabled(self, value: bool):
        self.com_object.StyleSheetEnabled = value

    @property
    def test_run(self) -> int:
        return self.com_object.TestRun

    @test_run.setter
    def test_run(self, value: int):
        self.com_object.TestRun = value

    @property
    def use_joint_report(self) -> bool:
        return self.com_object.UseJointReport

    @use_joint_report.setter
    def use_joint_report(self, value: bool):
        self.com_object.UseJointReport = value

    def wait_for_report_generation(self, timeout: int = 10) -> bool:
        return DoEventsUntil(lambda: self.test_configuration_report_events.SUCCESS, timeout, "Test Configuration Report Generation")
