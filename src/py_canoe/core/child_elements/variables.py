from collections.abc import Iterator

from py_canoe.core.child_elements.variable import Variable


class Variables:
    def __init__(self, com_object, namespace_name: str | None = None):
        self.com_object = com_object
        self.namespace_name = namespace_name

    @property
    def count(self):
        return self.com_object.Count

    def item(self, index: int, enable_events: bool = True) -> 'Variable':
        return Variable(
            self.com_object.Item(index),
            enable_events=enable_events,
            namespace_name=self.namespace_name,
        )

    def iter_items(self, enable_events: bool = False) -> Iterator['Variable']:
        for index in range(1, self.count + 1):
            yield self.item(index, enable_events=enable_events)

    def fetch_all(self) -> list['Variable']:
        return list(self.iter_items())

    def add(self, name: str):
        return self.com_object.Add(name)

    def add_ex(self, name: str, initial_value: float, min_value: float, max_value: float):
        return self.com_object.AddEx(name, initial_value, min_value, max_value)

    def add_writeable(self, name: str, initial_value: float):
        return self.com_object.AddWriteable(name, initial_value)

    def add_writable_ex(self, name: str, initial_value: float, min_value: float | None = None, max_value: float | None = None):
        return self.com_object.AddWritableEx(name, initial_value, min_value, max_value)

    def remove(self, variable):
        return self.com_object.Remove(variable)
