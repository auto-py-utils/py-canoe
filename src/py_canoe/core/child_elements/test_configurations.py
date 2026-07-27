import win32com.client

from py_canoe.core.child_elements.test_configuration import TestConfiguration
from py_canoe.core.child_elements.test_unit import TestUnit
from py_canoe.core.child_elements.test_tree_elements import TestTreeElements


class TestConfigurations:
    """The TestConfigurations object represents the test configurations within CANoe's test setup."""
    def __init__(self, com_object):
        self.com_object = win32com.client.Dispatch(com_object)

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int) -> TestConfiguration:
        return TestConfiguration(self.com_object.Item(index))

    def add(self, name: str) -> 'TestConfiguration':
        return TestConfiguration(self.com_object.Add(name))

    def remove(self, index: int, prompt_user=False) -> None:
        self.com_object.Remove(index, prompt_user)

    def fetch_all_test_configurations(self) -> dict[str, TestConfiguration]:
        test_configurations = dict()
        for index in range(1, self.count + 1):
            tc_inst = self.item(index)
            test_configurations[tc_inst.name] = tc_inst
        return test_configurations

    def __get_elements_or_cases(self, title:str):
        test_elements_or_cases = {}
        test_confs = self.fetch_all_test_configurations()
        for t_conf_name in test_confs.keys():
            test_units_obj: dict[str, TestUnit] = test_confs[t_conf_name].test_units.fetch_all_test_units()
            for tn_name in test_units_obj.keys():
                test_elements: TestTreeElements= test_units_obj[tn_name].elements
                if title == "elements":
                    test_elements_or_cases[tn_name] = test_elements.fetch_all_test_tree_elements()
                elif title == "case":
                    test_elements.get_test_tree_element_cases(test_elements_or_cases)
        return test_elements_or_cases
    
    def get_top_test_configurations_elements(self) -> dict:
        return self.__get_elements_or_cases("elements")
    
    def get_all_test_configurations_cases(self) -> dict:
        return self.__get_elements_or_cases("case")
