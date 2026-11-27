from collections.abc import Iterator

from py_canoe.core.child_elements.test_tree_element import (
    TestTreeElement,
    TestTreeElementType,
)
from py_canoe.core.com_session import dispatch_com_object


class TestTreeElements:
    """The TestTreeElements object represents a collection of test tree elements."""

    def __init__(self, com_object):
        self.com_object = dispatch_com_object(com_object)

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int) -> TestTreeElement:
        return TestTreeElement(self.com_object.Item(index))

    def iter_items(self) -> Iterator[TestTreeElement]:
        for index in range(1, self.count + 1):
            yield self.item(index)

    def fetch_all_test_tree_elements(self) -> dict[str, TestTreeElement]:
        return {element.caption: element for element in self.iter_items()}

    def __traverse_and_collect(self, ttes_obj: 'TestTreeElements', test_cases: dict):
        for tc_name, tte_obj in ttes_obj.fetch_all_test_tree_elements().items():
            if (tte_obj.type == TestTreeElementType.TEST_GROUP) or (tte_obj.type == TestTreeElementType.TEST_FIXTURE):
                if tte_obj.elements.count > 0:
                    self.__traverse_and_collect(tte_obj.elements, test_cases)
            else:
                test_cases[tc_name] = {"tte_obj": tte_obj}
            
    def get_test_tree_element_cases(self, test_cases: dict):
        self.__traverse_and_collect(self, test_cases)