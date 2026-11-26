from collections.abc import Iterator

from py_canoe.core.child_elements.database import Database


class Databases:
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def count(self) -> int:
        return self.com_object.Count

    def iter_items(self) -> Iterator[Database]:
        for index in range(1, self.count + 1):
            yield Database(self.com_object.Item(index))

    def item(self, index: int | None = None) -> 'Database | list[Database]':
        if index is None:
            return list(self.iter_items())
        return Database(self.com_object.Item(index))

    def add(self, full_name: str) -> 'Database':
        return Database(self.com_object.Add(full_name))

    def add_network(self, database_name: str, network_name: str) -> 'Database':
        return Database(self.com_object.AddNetwork(database_name, network_name))

    def remove(self, index: int) -> None:
        self.com_object.Remove(index)
