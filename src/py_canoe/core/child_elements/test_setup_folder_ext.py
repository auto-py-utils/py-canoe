import win32com.client

from py_canoe.core.child_elements.test_modules import TestModules
from py_canoe.core.child_elements.test_report import TestReport
from py_canoe.helpers.common import logger


class TestSetupFolderExt:
    """The TestSetupFolderExt object represents a directory in CANoe's test setup.

    This is the preferred object for test setup folders (replaces the
    deprecated TestSetupFolder object). Only this object provides access to
    all existing properties and methods.
    """

    def __init__(self, com_object) -> None:
        self.com_object = win32com.client.Dispatch(com_object)

    @property
    def enabled(self) -> bool:
        return self.com_object.Enabled

    @enabled.setter
    def enabled(self, enabled: bool):
        self.com_object.Enabled = enabled

    @property
    def name(self) -> str:
        return self.com_object.Name

    @name.setter
    def name(self, value: str) -> None:
        """Renames the test setup folder.

        Note: Although the CANoe help marks ``Name`` as read-only, it has
        been verified on CANoe 18 that assigning a value renames the folder.
        """
        old_name = self.com_object.Name
        self.com_object.Name = value
        logger.info(f'TestSetupFolderExt renamed: "{old_name}" -> "{value}"')

    @property
    def folders(self):
        from py_canoe.core.child_elements.test_setup_folders import TestSetupFolders
        return TestSetupFolders(self.com_object.Folders)

    @property
    def test_modules(self) -> 'TestModules':
        return TestModules(self.com_object.TestModules)

    @property
    def report(self) -> TestReport:
        """Returns a TestReport object for this folder.

        The wrapper (and its COM event sink) is cached after first access.
        """
        if getattr(self, "_report", None) is None:
            self._report = TestReport(self.com_object.Report)
        return self._report

    def execute_all(self):
        self.com_object.ExecuteAll()

    def stop_sequence(self):
        self.com_object.StopSequence()
