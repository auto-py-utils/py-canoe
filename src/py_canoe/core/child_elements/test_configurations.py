
import win32com.client

from py_canoe.core.child_elements.test_configuration import TestConfiguration


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
