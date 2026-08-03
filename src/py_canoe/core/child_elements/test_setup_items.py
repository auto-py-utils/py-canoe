from __future__ import annotations

import os

from py_canoe.core.child_elements.test_module import TestModule
from py_canoe.core.child_elements.test_setup_item import TestSetupItem
from py_canoe.core.child_elements.test_setup_folder import TestSetupFolder
from py_canoe.helpers.common import logger


class TestSetupItems:
    """The TestSetupItems object represents the test nodes and directories in a test environment or in a test setup directory.

    .. deprecated::
        This object is deprecated. Use TestSetupFolders and TestModules instead.
    """

    __test__ = False

    def __init__(self, com_object) -> None:
        self.com_object = com_object

    @property
    def count(self) -> int:
        """Returns the number of test setup items inside the collection."""
        return self.com_object.Count

    def item(self, index: int = None) -> 'TestSetupItem | list[TestSetupItem]':
        """Returns a test setup item at the given index.

        The returned item can be either a TestSetupFolder or a TestModule object.

        Args:
            index: The 1-based index of the item to retrieve. If None, returns all items.

        Returns:
            A TestSetupItem (TestModule or TestSetupFolder) wrapping the COM object,
            or a list of them when index is None.
        """
        if index is None:
            return [self._wrap(self.com_object.Item(i)) for i in range(1, self.count + 1)]
        return self._wrap(self.com_object.Item(index))

    def _wrap(self, com_obj) -> TestSetupItem:
        """Wraps a COM test setup item into the appropriate concrete class.

        A test setup item is either a TestModule or a TestSetupFolder.
        TestSetupFolder exposes a Folders/TestModules collection, while
        TestModule exposes a Sequence. We use the presence of the Folders
        property to distinguish them.
        """
        try:
            # TestSetupFolder has a Folders collection
            com_obj.Folders
            return TestSetupFolder(com_obj)
        except AttributeError:
            return TestModule(com_obj)

    def add_folder(self, name: str) -> TestSetupFolder:
        """Adds a directory to a test environment or a directory in the test setup.

        Args:
            name: The name of the new directory.

        Returns:
            The newly created TestSetupFolder COM object.
        """
        folder = TestSetupFolder(self.com_object.AddFolder(name))
        logger.info(f'TestSetupItems: added folder "{name}".')
        return folder

    def add_test_module(self, full_name: str, name: str = None) -> TestModule:
        """Adds a test module to a test environment or a directory in the test setup.

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
        # The COM interface expects a valid file path (e.g. a .can or .tse file).
        # Fail early with a clear message if the path is not absolute or does not exist,
        # so users don't get a cryptic COM 'File not found!' error.
        if not os.path.isabs(full_name):
            logger.warning(
                f'add_test_module: "{full_name}" is not an absolute path. '
                f'The path is resolved relative to the current CANoe configuration.'
            )
        elif not os.path.exists(full_name):
            raise FileNotFoundError(
                f'add_test_module: file not found: "{full_name}". '
                f'Pass the full path to a CAPL program (.can) or XML test description '
                f'(.tse/.stse/.vxt) file, not a module name.'
            )
        module = TestModule(self.com_object.AddTestModule(full_name))
        if name is not None:
            module.name = name
            logger.info(
                f'TestSetupItems: added test module from "{full_name}" '
                f'with custom name "{name}".'
            )
        else:
            logger.info(
                f'TestSetupItems: added test module from "{full_name}" '
                f'as "{module.name}".'
            )
        return module

    def remove(self, index) -> None:
        """Removes a test module or a directory from a test environment or a directory in the test setup.

        Args:
            index: The index of the object to be removed. Can be either the number or the name of the element.
        """
        self.com_object.Remove(index)
        logger.info(f'TestSetupItems: removed item at index/name "{index}".')

    def fetch_all_items(self) -> list:
        """Fetches all test setup items from the collection.

        Returns:
            A list of TestSetupItem objects.
        """
        items = []
        for index in range(1, self.count + 1):
            items.append(self.item(index))
        return items
