from collections.abc import Iterator

from py_canoe.core.child_elements.channel import Channel


class Channels:
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def count(self) -> int:
        return self.com_object.Count

    def iter_items(self) -> Iterator[Channel]:
        for index in range(1, self.count + 1):
            yield Channel(self.com_object.Item(index))

    def item(self, index: int | None = None) -> Channel | list[Channel]:
        if index is None:
            return list(self.iter_items())
        else:
            return Channel(self.com_object.Item(index))

    def add(self, type: int, number: int) -> Channel:
        return Channel(self.com_object.Add(type, number))

    def remove(self, index: int):
        self.com_object.Remove(index)
