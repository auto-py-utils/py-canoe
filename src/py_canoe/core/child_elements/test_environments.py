from collections.abc import Iterator

from py_canoe.core.child_elements.test_environment import TestEnvironment
from py_canoe.core.com_session import dispatch_com_object


class TestEnvironments:
    """The TestEnvironments object represents the test environments within CANoe's test setup."""
    def __init__(self, com_object):
        self.com_object = dispatch_com_object(com_object)

    @property
    def count(self) -> int:
        return self.com_object.Count
    
    def iter_items(self) -> Iterator[TestEnvironment]:
        for index in range(1, self.count + 1):
            yield TestEnvironment(self.com_object.Item(index))

    @property
    def item(self) -> list[TestEnvironment]:
        return list(self.iter_items())

    def add(self, name: str) -> 'TestEnvironment':
        for te in self.iter_items():
            if te.name == name:
                return None
        return TestEnvironment(self.com_object.Add(name))

    def remove(self, index: int, prompt_user=False) -> None:
        self.com_object.Remove(index, prompt_user)

    def fetch_all_test_environments(self) -> dict['str': 'TestEnvironment']:
        test_environments = {}
        for index in range(1, self.count + 1):
            te_inst = TestEnvironment(self.com_object.Item(index))
            test_environments[te_inst.name] = te_inst
        return test_environments
