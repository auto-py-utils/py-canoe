import os

from py_canoe.core.child_elements.test_library import TestLibrary
from py_canoe.helpers.common import logger


class TestLibraries:
    """The TestLibraries object represents the test case files that are used
    in XML or .NET test modules.

    Properties:
        count: Returns the number of test libraries contained (read-only).

    Methods:
        add: Adds a test case file to a test module.
        remove: Removes a test case file from a test module.
        item: Returns a TestLibrary object from the collection.
        fetch_all: Returns all TestLibrary objects as a list.
    """

    __test__ = False

    def __init__(self, com_object) -> None:
        self.com_object = com_object

    @property
    def count(self) -> int:
        """Returns the number of test libraries contained."""
        return self.com_object.Count

    def item(self, index: int | None = None) -> TestLibrary | list[TestLibrary]:
        """Returns a TestLibrary object from the collection.

        Args:
            index: The 1-based index of the item to retrieve.

        Returns:
            The TestLibrary at the given index.
        """
        if index is None:
            return [TestLibrary(self.com_object.Item(i)) for i in range(1, self.count + 1)]
        return TestLibrary(self.com_object.Item(index))

    def add(self, full_name: str) -> TestLibrary:
        """Adds a test case file to a test module.

        Note: Test case files can only be added to XML test modules.
        Calling this function will fail when working with CAPL test modules.

        Args:
            full_name: The absolute path of the test case file to be added.

        Returns:
            The newly created TestLibrary object.

        Raises:
            FileNotFoundError: If the given absolute path does not exist.
        """
        if not os.path.isabs(full_name):
            logger.warning(
                f'TestLibraries.add: "{full_name}" is not an absolute path. '
                f'The path is resolved relative to the current CANoe configuration.'
            )
        elif not os.path.exists(full_name):
            raise FileNotFoundError(
                f'TestLibraries.add: file not found: "{full_name}". '
                f'Pass the absolute path of a test case file.'
            )
        library = TestLibrary(self.com_object.Add(full_name))
        logger.info(f'TestLibraries: added test case file "{full_name}".')
        return library

    def remove(self, index) -> None:
        """Removes a test case file from a test module.

        Args:
            index: The index of the object to be removed. This can either be
                   the number (starting with 1), the filename (unambiguous
                   filenames only) or the complete path of the file.
        """
        self.com_object.Remove(index)
        logger.info(f'TestLibraries: removed test case file at index/name "{index}".')

    def fetch_all(self) -> list:
        """Fetches all TestLibrary objects from the collection.

        Returns:
            A list of TestLibrary objects.
        """
        libraries = []
        for index in range(1, self.count + 1):
            libraries.append(self.item(index))
        return libraries
