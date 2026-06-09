from py_canoe.core.child_elements.environment_variable import EnvironmentVariable


class EnvironmentArray:
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int) -> 'EnvironmentVariable':
        return EnvironmentVariable(self.com_object.Item(index))
