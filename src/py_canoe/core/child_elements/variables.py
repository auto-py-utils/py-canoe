from typing import Union
from py_canoe.core.child_elements.variable import Variable


class Variables:
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def count(self):
        return self.com_object.Count

    def item(self, index: int, enable_events: bool = True) -> 'Variable':
        return Variable(self.com_object.Item(index), enable_events=enable_events)

    def fetch_all(self) -> list['Variable']:
        result = []
        count = self.count
        for i in range(1, count + 1):
            result.append(self.item(i, enable_events=False))
        return result

    def add(self, name: str):
        return self.com_object.Add(name)

    def add_ex(self, name: str, initial_value: Union[int, float], min_value: Union[int, float], max_value: Union[int, float]):
        return self.com_object.AddEx(name, initial_value, min_value, max_value)

    def add_writeable(self, name: str, initial_value: Union[int, float]):
        return self.com_object.AddWriteable(name, initial_value)

    def add_writable_ex(self, name: str, initial_value: Union[int, float], min_value: Union[int, float] = None, max_value: Union[int, float] = None):
        return self.com_object.AddWritableEx(name, initial_value, min_value, max_value)

    def remove(self, variable):
        return self.com_object.Remove(variable)
