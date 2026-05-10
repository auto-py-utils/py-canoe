from py_canoe.core.child_elements.bus import Bus


class Buses:
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int) -> 'Bus':
        return Bus(self.com_object.Item(index))
