import win32com.client

from py_canoe.core.child_elements.test_tree_element import TestTreeElement, TestTreeElementType


class TestTreeElements:
    """The TestTreeElements object represents a collection of test tree elements."""

    def __init__(self, com_object):
        self.com_object = win32com.client.Dispatch(com_object)

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int) -> TestTreeElement:
        return TestTreeElement(self.com_object.Item(index))

    def fetch_all_test_tree_elements(self) -> dict[str, TestTreeElement]:
        test_tree_elements = dict()
        for index in range(1, self.count + 1):
            tte_inst = self.item(index)
            test_tree_elements[tte_inst.caption] = tte_inst
        return test_tree_elements

    def __traverse_and_collect(self, ttes_obj: 'TestTreeElements', test_cases: dict):
        for tc_name, tte_obj in ttes_obj.fetch_all_test_tree_elements().items():
            if (tte_obj.type == TestTreeElementType.TEST_GROUP) or (tte_obj.type == TestTreeElementType.TEST_FIXTURE):
                if tte_obj.elements.count > 0:
                    self.__traverse_and_collect(tte_obj.elements, test_cases)
            else:
                test_cases[tc_name] = {"tte_obj": tte_obj}
            
    def get_test_tree_element_cases(self, test_cases: dict):
        self.__traverse_and_collect(self, test_cases)