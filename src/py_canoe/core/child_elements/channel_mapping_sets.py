

from typing import List

from py_canoe.helpers.bus_type import BusType
from py_canoe.helpers.common import logger


class ChannelMappingSet:
    """The ChannelMappingSet object represents a single Channel Mapping Set
    in a Measurement Setup. It allows setting or returning the channel mapping
    configuration for the offline source.
    """

    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def id(self) -> str:
        """Returns the unique ID of the channel mapping set."""
        return self.com_object.Id

    @property
    def name(self) -> str:
        """Returns the name of the channel mapping set."""
        return self.com_object.Name

    @property
    def description(self) -> str:
        """Returns the description of the channel mapping set."""
        return self.com_object.Description

    def clear_mapping_table(self) -> None:
        """Removes all channel mappings from the channel mapping set."""
        try:
            self.com_object.ClearMappingTable()
            logger.info(f'Channel mapping set "{self.name}" mapping table cleared.')
        except Exception as e:
            logger.error(f'Error clearing mapping table for "{self.name}": {e}')

    def copy(self) -> 'ChannelMappingSet':
        """Creates a copy of the channel mapping set.

        Returns:
            ChannelMappingSet: A new copy of this channel mapping set.
        """
        try:
            return ChannelMappingSet(self.com_object.Copy())
        except Exception as e:
            logger.error(f'Error copying channel mapping set "{self.name}": {e}')
            raise

    def get(self, bus_type: BusType, source: int) -> int:
        """Returns the destination channel number to which the source channel
        is mapped.

        The value 0 represents "ignore".

        Args:
            bus_type (BusType): The type of the bus (e.g. BusType.CAN).
            source (int): The source channel number.

        Returns:
            int: The destination channel number; 0 represents "ignore".
        """
        try:
            return self.com_object.Get(bus_type.value, source)
        except Exception as e:
            logger.error(f'Error getting channel mapping (bus_type={bus_type.name}, source={source}): {e}')
            raise

    def get_by_bus_name(self, bus_name: str, source: int) -> int:
        """Returns the destination channel number to which the source channel
        is mapped, identified by bus name.

        Args:
            bus_name (str): The name of the bus.
            source (int): The source channel number.

        Returns:
            int: The destination channel number; 0 represents "ignore".
        """
        try:
            return self.com_object.GetByBusName(bus_name, source)
        except Exception as e:
            logger.error(f'Error getting channel mapping (bus_name="{bus_name}", source={source}): {e}')
            raise

    def put(self, bus_type: BusType, source: int, destination: int) -> None:
        """Sets the destination channel number to which the source channel
        is mapped.

        Args:
            bus_type (BusType): The type of the bus (e.g. BusType.CAN).
            source (int): The source channel number.
            destination (int): The destination channel number.
        """
        try:
            self.com_object.Put(bus_type.value, source, destination)
            logger.info(f'Channel mapping set: bus_type={bus_type.name}, source={source} -> destination={destination}')
        except Exception as e:
            logger.error(f'Error putting channel mapping (bus_type={bus_type.name}, source={source}, dest={destination}): {e}')
            raise

    def put_by_bus_name(self, bus_name: str, source: int, destination: int) -> None:
        """Sets the destination channel number to which the source channel
        is mapped, identified by bus name.

        Args:
            bus_name (str): The name of the bus.
            source (int): The source channel number.
            destination (int): The destination channel number.
        """
        try:
            self.com_object.PutByBusName(bus_name, source, destination)
            logger.info(f'Channel mapping set: bus_name="{bus_name}", source={source} -> destination={destination}')
        except Exception as e:
            logger.error(f'Error putting channel mapping (bus_name="{bus_name}", source={source}, dest={destination}): {e}')
            raise




class ChannelMappingSets:
    """Python wrapper for CANoe COM ChannelMappingSets object.

    Represents a collection of ChannelMappingSet objects belonging to a
    Measurement Setup. Supports both COM-style 1-based access via ``item()``
    and Pythonic 0-based iteration via ``__len__`` / ``__getitem__`` /
    ``__iter__``.
    """

    def __init__(self, com_object):
        self.com_object = com_object

    def __len__(self) -> int:
        return self.com_object.Count if self.com_object else 0

    def __getitem__(self, index: int) -> 'ChannelMappingSet':
        if self.com_object is None or index < 0 or index >= len(self):
            raise IndexError("Index out of range")
        return ChannelMappingSet(self.com_object.Item(index + 1))

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    @property
    def count(self) -> int:
        """Returns the number of channel mapping sets in the collection."""
        return self.com_object.Count if self.com_object else 0

    def item(self, index: int | None = None) -> 'ChannelMappingSet' | List['ChannelMappingSet']:
        """Returns a ChannelMappingSet by 1-based index, or all mapping sets
        if *index* is ``None``.

        Args:
            index (int | None): 1-based index of the mapping set, or ``None``
                to return all mapping sets as a list.

        Returns:
            ChannelMappingSet or list[ChannelMappingSet]
        """
        if not self.com_object:
            return [] if index is None else None
        if index is None:
            return [ChannelMappingSet(self.com_object.Item(i + 1)) for i in range(self.com_object.Count)]
        if index < 1 or index > self.com_object.Count:
            raise IndexError(f"Index {index} out of range [1..{self.com_object.Count}]")
        return ChannelMappingSet(self.com_object.Item(index))