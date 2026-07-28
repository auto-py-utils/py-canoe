import win32com.client

from py_canoe.core.child_elements.test_environment import TestEnvironment

class TestEnvironments:
    """The TestEnvironments object represents the test environments within CANoe's test setup."""
    def __init__(self, com_object):
        self.com_object = win32com.client.Dispatch(com_object)

    @property
    def count(self) -> int:
        return self.com_object.Count
    
    @property
    def Item(self) -> list[TestEnvironment]:
        return [TestEnvironment(self.com_object.Item(index)) for index in range(1, self.count + 1)]

    def add(self, name: str) -> 'TestEnvironment':
        for te in self.Item:
            if te.name == name:
                return None
        return TestEnvironment(self.com_object.Add(name))

    def remove(self, index: int, prompt_user=False) -> None:
        self.com_object.Remove(index, prompt_user)

    def fetch_all_test_environments(self) -> dict['str': 'TestEnvironment']:
        test_environments = dict()
        for index in range(1, self.count + 1):
            te_inst = TestEnvironment(self.com_object.Item(index))
            test_environments[te_inst.name] = te_inst
        return test_environments
