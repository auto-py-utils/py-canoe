from typing import List

from py_canoe.core.child_elements.bus import Bus
from py_canoe.helpers.bus_type import BusType


class Buses:
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int | None = None) -> Bus | List[Bus]:
        if index is None:
            return [Bus(self.com_object.Item(i)) for i in range(1, self.count + 1)]
        else:
            return Bus(self.com_object.Item(index))
    
    def add(self, name: str, bus_type: BusType = BusType.CAN) -> 'Bus':
        """Adds a new bus with a specified type to the configuration. default bus_type is 1 (CAN).

        Args:
            name (str): The name of the new bus.
            bus_type (int): The type of the new bus (1 for CAN, 5 for LIN, 6 for MOST, 7 for FlexRay, 9 for J1708, 11 for Ethernet, 13 for WLAN).

        Returns:
            Bus: The newly added Bus object.
        """
        for index in range(1, self.count + 1):
            if self.item(index).name == name:
                return None # Bus with the same name already exists
        return Bus(self.com_object.AddWithType(name, bus_type.value))
    
    def remove(self, index: int = None, name: str = None) -> None:
        """Removes an existing bus.

        It is only possible to remove a bus when measurement is stopped and more than one bus is configured.

        Args:
            index (int, optional): The index of the bus to be removed. Defaults to None.
            name (str, optional): The name of the bus to be removed. Defaults to None.
        Raises:
            ValueError: If neither index nor name is provided.
        """
        if index is not None:
            self.com_object.Remove(index)
        elif name is not None:
            self.com_object.Remove(name)
        else:
            raise ValueError("Either index or name must be provided to remove a bus.")