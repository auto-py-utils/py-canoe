import win32com.client

from py_canoe.core.child_elements.test_module import TestModule
from py_canoe.core.child_elements.test_modules import TestModules
from py_canoe.core.child_elements.test_setup_folder import TestSetupFolder
from py_canoe.core.child_elements.test_setup_folders import TestSetupFolders
from py_canoe.core.child_elements.test_setup_items import TestSetupItems
from py_canoe.core.child_elements.test_report import TestReport


class TestEnvironment:
    """The TestEnvironment object represents a test environment in the test setup.

    Properties:
        enabled: Activates/deactivates the test environment.
        folders: Returns a TestSetupFolders collection.
        full_name: Returns the complete path to the test environment.
        items: Returns a TestSetupItems collection (deprecated).
        modified: Indicates whether the test environment has been changed since the last load/save.
        name: Returns the name of the test environment.
        path: Returns the path to the test environment.
        report: Returns a TestReport object.
        test_modules: Returns a TestModules collection.

    Methods:
        execute_all: Executes all test modules in the test environment (deprecated).
        save: Saves the test environment.
        save_as: Saves the test environment in older formats.
        stop_sequence: Stops the test sequence (deprecated).
        get_all_test_modules: Recursively fetches all test modules from all folders and items.
    """

    __test__ = False

    def __init__(self, com_object):
        self.com_object = win32com.client.Dispatch(com_object)

    @property
    def enabled(self) -> bool:
        """Activates/deactivates a test environment or returns whether the test environment
        is in an active/inactive state. Default value is False."""
        return self.com_object.Enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self.com_object.Enabled = value

    @property
    def folders(self) -> TestSetupFolders:
        """Returns a TestSetupFolders collection."""
        return TestSetupFolders(self.com_object.Folders)

    @property
    def full_name(self) -> str:
        """Returns the complete path to the test environment."""
        return self.com_object.FullName

    @property
    def items(self) -> TestSetupItems:
        """Returns a TestSetupItems collection (deprecated).

        Use folders and test_modules instead.
        """
        return TestSetupItems(self.com_object.Items)

    @property
    def modified(self) -> bool:
        """Indicates whether the test environment has been changed since the last time
        it has been loaded/saved."""
        return self.com_object.Modified

    @property
    def name(self) -> str:
        """Returns the name of the test environment."""
        return self.com_object.Name

    @property
    def path(self) -> str:
        """Returns the path to the test environment."""
        return self.com_object.Path

    @property
    def report(self) -> TestReport:
        """Returns a TestReport object for this test environment."""
        return TestReport(self.com_object.Report)

    @property
    def test_modules(self) -> TestModules:
        """Returns a TestModules collection."""
        return TestModules(self.com_object.TestModules)

    def execute_all(self) -> None:
        """Executes all test modules in the test environment.

        .. deprecated::
            Use TestModule.Start and the corresponding event handlers instead.
        """
        self.com_object.ExecuteAll()

    def save(self, name: str = None, prompt_user: bool = True) -> None:
        """Saves the test environment.

        Args:
            name: Sets the (new) path for the test environment, if applicable.
                  If no path is specified, the test environment is saved under its current name.
                  If it is not saved yet, the user will be prompted for a name.
            prompt_user: Indicates whether the user should intervene in error situations.
                         Default is True.
        """
        if name is None:
            self.com_object.Save()
        else:
            self.com_object.Save(name, prompt_user)

    def save_as(self, name: str, major: int, minor: int, prompt_user: bool = True) -> None:
        """Saves the test environment in older formats.

        Args:
            name: The path of the file in which the test environment will be saved.
            major: Prefix of the version number (e.g. 5 for version 5.1).
            minor: Suffix of the version number (e.g. 1 for version 5.1).
                   Use 0, 0 to save in the current application version format.
            prompt_user: Indicates whether the user should intervene in error situations.
                         Default is True.
        """
        self.com_object.SaveAs(name, major, minor, prompt_user)

    def stop_sequence(self) -> None:
        """Stops the test sequence.

        .. deprecated::
            Use TestModule.Stop instead.
        """
        self.com_object.StopSequence()

    def get_all_test_modules(self) -> dict:
        """Recursively fetches all test modules from all folders and items in this test environment.

        Returns:
            A dict mapping test module names to TestModule objects.
        """
        all_test_modules = {}

        # Fetch test modules directly in this test environment
        for tm_name, tm_inst in self.test_modules.fetch_test_modules().items():
            all_test_modules[tm_name] = tm_inst

        # Recursively fetch test modules from all folders
        for folder_name, folder_inst in self.folders.fetch_test_setup_folders().items():
            for tm_name, tm_inst in self.__fetch_test_modules_from_folder(folder_inst).items():
                all_test_modules[tm_name] = tm_inst

        return all_test_modules

    def __fetch_test_modules_from_folder(self, folder) -> dict:
        """Recursively fetches test modules from a TestSetupFolderExt object."""
        all_test_modules = {}

        # Fetch test modules directly in this folder
        for tm_name, tm_inst in folder.test_modules.fetch_test_modules().items():
            all_test_modules[tm_name] = tm_inst

        # Recursively fetch test modules from sub-folders
        for sub_folder_name, sub_folder_inst in folder.folders.fetch_test_setup_folders().items():
            for tm_name, tm_inst in self.__fetch_test_modules_from_folder(sub_folder_inst).items():
                all_test_modules[tm_name] = tm_inst

        return all_test_modules

    def add_test_module(self, full_name: str, name: str = None) -> TestModule:
        """Adds a test module to the test environment.

        The path can be absolute or relative to the current CANoe configuration.

        Args:
            full_name: The path of the CAPL program (.can) or the XML test description
                       (.tse/.stse/.vxt) for the test module. This must be a valid file path,
                       not a module name.
            name: Optional custom name for the test module. If not None, the module
                  is renamed immediately after being added.

        Returns:
            The newly created TestModule object.

        Raises:
            FileNotFoundError: If the given path does not exist.
        """
        return self.items.add_test_module(full_name, name)

    def add_folder(self, name: str) -> TestSetupFolder:
        """Adds a folder to the test environment.

        Args:
            name: The name of the new folder.

        Returns:
            The newly created TestSetupFolder object.
        """
        return self.items.add_folder(name)
