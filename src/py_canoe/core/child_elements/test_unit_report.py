from py_canoe.core.com_session import dispatch_com_object, with_com_events
from py_canoe.helpers.common import DoEventsUntil


class TestUnitReportEvents:
    """Event handlers for TestUnitReport COM object events."""

    def __init__(self):
        self.SUCCESS = False
        self.SOURCE_FULL_NAME = ""
        self.GENERATED_FULL_NAME = ""

    def OnGenerated(self, success: bool, source_full_name: str, generated_full_name: str):
        self.SUCCESS = success
        self.SOURCE_FULL_NAME = source_full_name
        self.GENERATED_FULL_NAME = generated_full_name


class TestUnitReport:
    """The TestUnitReport object represents the reporting settings of a test unit."""

    def __init__(self, com_object):
        self.com_object = dispatch_com_object(com_object)
        self.events: TestUnitReportEvents = with_com_events(self.com_object, TestUnitReportEvents)

    @property
    def enabled(self) -> bool:
        return self.com_object.Enabled

    @enabled.setter
    def enabled(self, value: bool):
        self.com_object.Enabled = value

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

    def wait_for_report_generation(self, timeout: int = 10) -> bool:
        return DoEventsUntil(lambda: self.events.SUCCESS, timeout, "Test Unit Report Generation")

