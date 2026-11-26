from collections.abc import Iterator

from py_canoe.core.child_elements.test_unit import TestUnit
from py_canoe.core.com_session import dispatch_com_object


class TestUnits:
    """The TestUnits object represents the collection of test units of a single test configuration."""

    def __init__(self, com_object):
        self.com_object = dispatch_com_object(com_object)

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int) -> TestUnit:
        return TestUnit(self.com_object.Item(index))

    def iter_items(self) -> Iterator[TestUnit]:
        for index in range(1, self.count + 1):
            yield self.item(index)

    def add(self, path: str) -> TestUnit:
        return TestUnit(self.com_object.Add(path))

    def remove(self, index: int):
        self.com_object.Remove(index)

    def fetch_all_test_units(self) -> dict[str, TestUnit]:
        return {unit.name: unit for unit in self.iter_items()}

