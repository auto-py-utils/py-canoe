from enum import Enum
import win32com.client


class TestTreeElementType(Enum):
    """Enum representing the types of test tree element."""
    TEST_TYPE_RESERVED = 0
    TEST_CONFIGURATION = 1
    TEST_UNIT = 2
    TEST_GROUP = 3
    TEST_SEQUENCE = 4
    TEST_CASE = 5
    TEST_FIXTURE = 6
    TEST_CASE_LIST = 7
    TEST_SEQUENCE_LIST = 8


class TestTreeElement:
    """The TestTreeElement object represents a single element in the test tree."""

    def __init__(self, com_object):
        self.com_object = win32com.client.Dispatch(com_object)

    def __getattr__(self, item):
        return getattr(self.com_object, item)

    @property
    def caption(self) -> str:
        return self.com_object.Caption

    @property
    def enabled(self) -> bool:
        return self.com_object.Enabled

    @enabled.setter
    def enabled(self, value: bool):
        self.com_object.Enabled = value

    @property
    def id(self) -> str:
        return self.com_object.Id

    @property
    def verdict(self) -> int:
        return self.com_object.Verdict

    @property
    def type(self) -> TestTreeElementType:
        return TestTreeElementType(self.com_object.Type)

    @property
    def elements(self):
        # Imported lazily to avoid circular imports
        from py_canoe.core.child_elements.test_tree_elements import TestTreeElements

        return TestTreeElements(self.com_object.Elements)

