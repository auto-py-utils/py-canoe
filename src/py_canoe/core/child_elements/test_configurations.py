from collections.abc import Iterator

from py_canoe.core.child_elements.test_configuration import TestConfiguration
from py_canoe.core.child_elements.test_tree_elements import TestTreeElements
from py_canoe.core.child_elements.test_unit import TestUnit
from py_canoe.core.com_session import dispatch_com_object


class TestConfigurations:
    """The TestConfigurations object represents the test configurations within CANoe's test setup."""
    def __init__(self, com_object):
        self.com_object = dispatch_com_object(com_object)

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int) -> TestConfiguration:
        return TestConfiguration(self.com_object.Item(index))

    def iter_items(self) -> Iterator[TestConfiguration]:
        for index in range(1, self.count + 1):
            yield self.item(index)

    def add(self, name: str) -> 'TestConfiguration':
        return TestConfiguration(self.com_object.Add(name))

    def remove(self, index: int, prompt_user=False) -> None:
        self.com_object.Remove(index, prompt_user)

    def fetch_all_test_configurations(self) -> dict[str, TestConfiguration]:
        return {
            configuration.name: configuration
            for configuration in self.iter_items()
        }

    def __get_elements_or_cases(self, title:str):
        test_elements_or_cases = {}
        test_confs = self.fetch_all_test_configurations()
        for test_configuration in test_confs.values():
            test_units_obj: dict[str, TestUnit] = test_configuration.test_units.fetch_all_test_units()
            for tn_name, test_unit in test_units_obj.items():
                test_elements: TestTreeElements= test_unit.elements
                if title == "elements":
                    test_elements_or_cases[tn_name] = test_elements.fetch_all_test_tree_elements()
                elif title == "case":
                    test_elements.get_test_tree_element_cases(test_elements_or_cases)
        return test_elements_or_cases
    
    def get_top_test_configurations_elements(self) -> dict:
        return self.__get_elements_or_cases("elements")
    
    def get_all_test_configurations_cases(self) -> dict:
        return self.__get_elements_or_cases("case")
