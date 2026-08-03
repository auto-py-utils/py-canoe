import win32com.client

from py_canoe.helpers.common import logger


class TestSetupItem:
    """The TestSetupItem object represents a single item in a test setup collection.

    A TestSetupItem can be either a TestModule or a TestSetupFolder object.
    Both TestModule and TestSetupFolder inherit from this class.
    """

    __test__ = False

    def __init__(self, com_object):
        self.com_object = com_object

    def __getattr__(self, item):
        return getattr(self.com_object, item)

    @property
    def name(self) -> str:
        """Returns the name of the test setup item."""
        return self.com_object.Name

    @name.setter
    def name(self, value: str) -> None:
        """Renames the test setup item.

        Note: Although the CANoe help marks ``Name`` as read-only,
        it has been verified on CANoe 18 that assigning a value renames
        the item in the Test Setup (the new name is saved with the .cfg).
        """
        old_name = self.com_object.Name
        self.com_object.Name = value
        logger.info(f'TestSetupItem renamed: "{old_name}" -> "{value}"')
