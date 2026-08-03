import win32com.client


class TestReportEvents:
    """Event handlers for TestReport COM object events."""

    __test__ = False

    def __init__(self):
        self.REPORT_GENERATED = False
        self.SUCCESS = False
        self.SOURCE_FULL_NAME = ""
        self.GENERATED_FULL_NAME = ""

    def OnReportGenerated(self, success, source_full_name, generated_full_name):
        self.REPORT_GENERATED = True
        self.SUCCESS = success
        self.SOURCE_FULL_NAME = source_full_name
        self.GENERATED_FULL_NAME = generated_full_name


class TestReport:
    """The TestReport object represents the reporting settings of a test environment,
    of a test module or of a directory in the test setup."""

    __test__ = False

    def __init__(self, com_object):
        self.com_object = win32com.client.Dispatch(com_object)
        self.test_report_events: TestReportEvents = win32com.client.WithEvents(
            self.com_object, TestReportEvents
        )

    @property
    def auto_numbering(self) -> bool:
        """Returns/sets whether the filename of the report shall be numbered automatically."""
        return self.com_object.AutoNumbering

    @auto_numbering.setter
    def auto_numbering(self, value: bool) -> None:
        self.com_object.AutoNumbering = value

    @property
    def enabled(self) -> bool:
        """Activates/deactivates the test report.

        Note: The reporting of test environments and directories is always activated (TRUE).
        """
        return self.com_object.Enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self.com_object.Enabled = value

    @property
    def filter_settings(self):
        """Returns a ReportFilterSettings object (only available in test module context)."""
        return self.com_object.FilterSettings

    @property
    def full_name(self) -> str:
        """Sets or determines the complete path to the test report."""
        return self.com_object.FullName

    @full_name.setter
    def full_name(self, value: str) -> None:
        self.com_object.FullName = value

    @property
    def last_written_full_name(self) -> str:
        """Provides the full path and filename of the last written test report file.

        Returns an empty string when no such file is known.
        """
        return self.com_object.LastWrittenFullName

    @property
    def name(self) -> str:
        """Returns the filename of the test report without path and filename extension."""
        return self.com_object.Name

    @property
    def path(self) -> str:
        """Returns the path of the test report."""
        return self.com_object.Path

    @property
    def style_sheet(self) -> str:
        """Sets/returns which XSLT file will be used for the automated conversion of the XML test report."""
        return self.com_object.StyleSheet

    @style_sheet.setter
    def style_sheet(self, value: str) -> None:
        self.com_object.StyleSheet = value

    @property
    def style_sheet_enabled(self) -> bool:
        """Sets/returns whether the XML test report will automatically be converted into an HTML file."""
        return self.com_object.StyleSheetEnabled

    @style_sheet_enabled.setter
    def style_sheet_enabled(self, value: bool) -> None:
        self.com_object.StyleSheetEnabled = value

    def generate_report_async(self) -> None:
        """Creates a test report in a background thread not blocking the GUI.

        After finishing the generation of the HTML report the OnReportGenerated event is sent.
        """
        self.com_object.GenerateReportAsync()
