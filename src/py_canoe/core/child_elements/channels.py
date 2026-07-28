from py_canoe.core.child_elements.channel import Channel


class Channels:
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int | None = None) -> 'Channel' | list['Channel']:
        if index is None:
            return [Channel(self.com_object.Item(i)) for i in range(1, self.count + 1)]
        else:
            return Channel(self.com_object.Item(index))

    def add(self, type: int, number: int) -> 'Channel':
        return Channel(self.com_object.Add(type, number))

    def remove(self, index: int):
        self.com_object.Remove(index)
