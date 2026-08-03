from py_canoe.core.child_elements.test_setup_item import TestSetupItem
from py_canoe.core.child_elements.test_report import TestReport


class TestSetupFolder(TestSetupItem):
    """The TestSetupFolder object represents a folder in the Test Setup.

    Inherits from TestSetupItem.

    .. deprecated::
        This COM object is deprecated. Use TestSetupFolders (returning
        TestSetupFolderExt) and TestModules instead. Only those objects
        provide access to all existing properties and methods.

    Properties:
        enabled: Activates/deactivates the folder. Default is False.
        items: Returns a TestSetupItems collection (deprecated).
        name: Returns the name of the folder.
        report: Returns a TestReport object.

    Methods:
        execute_all: Executes all test modules in the directory (deprecated).
    """

    __test__ = False

    def __init__(self, com_object):
        super().__init__(com_object)

    @property
    def enabled(self) -> bool:
        """Activates/deactivates the folder or returns whether it is active.

        The initial value is False.
        """
        return self.com_object.Enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self.com_object.Enabled = value

    @property
    def items(self):
        """Returns a TestSetupItems collection (deprecated).

        Use the TestSetupFolders and TestModules objects instead.
        """
        from py_canoe.core.child_elements.test_setup_items import TestSetupItems
        return TestSetupItems(self.com_object.Items)

    @property
    def report(self) -> TestReport:
        """Returns a TestReport object for this folder.

        The wrapper (and its COM event sink) is cached after first access.
        """
        if getattr(self, "_report", None) is None:
            self._report = TestReport(self.com_object.Report)
        return self._report

    def execute_all(self) -> None:
        """Consecutively executes all test modules in the directory.

        .. deprecated::
            Use TestModule.Start and the corresponding event handlers instead.
        """
        self.com_object.ExecuteAll()
