from typing import TYPE_CHECKING

from py_canoe.core.child_elements.channel_mapping_sets import ChannelMappingSet, ChannelMappingSets
if TYPE_CHECKING:
    from py_canoe.core.configuration import Configuration

import os
import win32com.client

from py_canoe.helpers.common import DoEventsUntil, logger, wait


class MeasurementSetup:
    """
    The MeasurementSetup object represents the Measurement Setup in CANoe.
    """
    def __init__(self, meas_com_object) -> None:
        self.com_object = win32com.client.Dispatch(meas_com_object)

    @property
    def animation_factor(self):
        return self.com_object.AnimationFactor

    @animation_factor.setter
    def animation_factor(self, value: int):
        self.com_object.AnimationFactor = value

    @property
    def bus_statistics(self):
        """Returns the BusStatistics object."""
        return self.com_object.BusStatistics

    @property
    def early_filtering(self):
        """Returns the EarlyFiltering object."""
        return self.com_object.EarlyFiltering

    @property
    def ethernet_statistics_sys_var_as_struct(self) -> bool:
        """Gets or sets whether Ethernet bus statistics system variables are
        grouped into a struct per channel and port.
        """
        return self.com_object.EthernetStatisticsSysVarAsStruct

    @ethernet_statistics_sys_var_as_struct.setter
    def ethernet_statistics_sys_var_as_struct(self, value: bool):
        self.com_object.EthernetStatisticsSysVarAsStruct = value

    @property
    def extended_ethernet_logging(self) -> bool:
        """Gets or sets the extended Ethernet logging parameter.
        Enables storage of subchannels and ports for network based mode.
        """
        return self.com_object.ExtendedEthernetLogging

    @extended_ethernet_logging.setter
    def extended_ethernet_logging(self, value: bool):
        self.com_object.ExtendedEthernetLogging = value

    @property
    def logging_collection(self):
        """Returns the LoggingCollection object."""
        return LoggingCollection(self.com_object.LoggingCollection)

    @property
    def offline_source_root(self):
        """Returns the root group of the offline sources.
        MeasurementSetup must be an offline Measurement Setup.
        """
        return self.com_object.OfflineSourceRoot

    @property
    def parallelization_level(self) -> int:
        return self.com_object.ParallelizationLevel

    @parallelization_level.setter
    def parallelization_level(self, level: int):
        self.com_object.ParallelizationLevel = level

    @property
    def source(self):
        """Returns the data source of the offline Measurement Setup."""
        return self.com_object.Source

    @property
    def video_windows(self):
        """Returns the VideoWindows object."""
        return self.com_object.VideoWindows

    @property
    def view_synchronization(self):
        """Returns the ViewSynchronization object."""
        return self.com_object.ViewSynchronization

    @property
    def working_mode(self) -> int:
        return self.com_object.WorkingMode

    @working_mode.setter
    def working_mode(self, mode: int):
        self.com_object.WorkingMode = mode


    def activate_end_block(self, name: str, activate: bool) -> None:
        """Activates or deactivates an end block with the given name.

        If multiple end blocks have the given name, all are activated/deactivated.

        Args:
            name: The name of the end block.
            activate: True to activate, False to deactivate.
        """
        try:
            self.com_object.ActivateEndBlock(name, activate)
            logger.info(f'End block "{name}" {"activated" if activate else "deactivated"}.')
        except Exception as e:
            logger.error(f'Error activating end block "{name}": {e}')
            raise

    def create_mapping_set(self, mapping_set_name: str) -> 'ChannelMappingSet':
        """Creates a new channel mapping set.

        MeasurementSetup must be an offline Measurement Setup.

        Args:
            mapping_set_name: The name of the new channel mapping set.

        Returns:
            ChannelMappingSet: The newly created channel mapping set.
        """
        try:
            return ChannelMappingSet(self.com_object.CreateMappingSet(mapping_set_name))
        except Exception as e:
            logger.error(f'Error creating mapping set "{mapping_set_name}": {e}')
            raise

    def export_mapping_sets(self, file_name: str) -> None:
        """Exports all channel mapping sets to a CHMAP file.

        MeasurementSetup must be an offline Measurement Setup.

        Args:
            file_name: Full path of the CHMAP file.
        """
        try:
            self.com_object.ExportMappingSets(file_name)
            logger.info(f'Mapping sets exported to "{file_name}".')
        except Exception as e:
            logger.error(f'Error exporting mapping sets: {e}')
            raise

    def get_all_mapping_sets(self) -> 'ChannelMappingSets':
        """Returns a collection of all channel mapping sets.

        MeasurementSetup must be an offline Measurement Setup.

        Returns:
            ChannelMappingSets: Collection of all mapping sets.
        """
        try:
            return ChannelMappingSets(self.com_object.GetAllMappingSets())
        except Exception as e:
            logger.warning(f'Unable to get mapping sets (offline setup only): {e}')
            return ChannelMappingSets(None)

    def get_mapping_set_by_id(self, mapping_set_id: str) -> 'ChannelMappingSet':
        """Returns the channel mapping set with the given ID.

        MeasurementSetup must be an offline Measurement Setup.

        Args:
            mapping_set_id: The unique ID of the channel mapping set.

        Returns:
            ChannelMappingSet: The matching channel mapping set.
        """
        try:
            return ChannelMappingSet(self.com_object.GetMappingSetById(mapping_set_id))
        except Exception as e:
            logger.error(f'Error getting mapping set by id "{mapping_set_id}": {e}')
            raise

    def get_mapping_set_by_name(self, mapping_set_name: str) -> 'ChannelMappingSet':
        """Returns the channel mapping set with the given name.

        If several channel mapping sets with this name exist, the first found
        set is returned. MeasurementSetup must be an offline Measurement Setup.

        Args:
            mapping_set_name: The name of the channel mapping set.

        Returns:
            ChannelMappingSet: The matching channel mapping set.
        """
        try:
            return ChannelMappingSet(self.com_object.GetMappingSetByName(mapping_set_name))
        except Exception as e:
            logger.error(f'Error getting mapping set by name "{mapping_set_name}": {e}')
            raise

    def import_mapping_sets(self, file_name: str, overwrite_existing: bool = False) -> 'ChannelMappingSets':
        """Imports channel mapping sets from a CHMAP file.

        MeasurementSetup must be an offline Measurement Setup.

        Args:
            file_name: Full path of the CHMAP file.
            overwrite_existing: If True, existing mapping sets with the same ID
                will be overwritten; if False, they are preserved.

        Returns:
            ChannelMappingSets: The imported mapping sets.
        """
        try:
            return ChannelMappingSets(self.com_object.ImportMappingSets(file_name, overwrite_existing))
        except Exception as e:
            logger.error(f'Error importing mapping sets from "{file_name}": {e}')
            raise

    def import_measurement_setup(self, cfg_path: str) -> None:
        """Imports the measurement setup from a configuration file.

        CAPL files and logging file paths are automatically adapted to the
        current configuration.

        Args:
            cfg_path: The path of the configuration file to import from.
        """
        try:
            self.com_object.ImportMeasurementSetup(cfg_path)
            logger.info(f'Measurement setup imported from "{cfg_path}".')
        except Exception as e:
            logger.error(f'Error importing measurement setup from "{cfg_path}": {e}')
            raise

    def remove_mapping_set(self, mapping_set: 'ChannelMappingSet') -> None:
        """Removes a channel mapping set.

        MeasurementSetup must be an offline Measurement Setup.

        Args:
            mapping_set: The ChannelMappingSet object to remove.
        """
        try:
            self.com_object.RemoveMappingSet(mapping_set.com_object if hasattr(mapping_set, 'com_object') else mapping_set)
            logger.info(f'Mapping set removed.')
        except Exception as e:
            logger.error(f'Error removing mapping set: {e}')
            raise


class LoggingCollection:
    """
    The LoggingCollection object is a collection of all Logging Blocks belonging to a Measurement Setup
    """
    def __init__(self, logging_collection_com):
        self.com_object = win32com.client.Dispatch(logging_collection_com)

    @property
    def count(self) -> int:
        return int(self.com_object.Count)

    def item(self, index: int) -> 'Logging':
        return Logging(self.com_object.Item(index))

    def add(self, full_name: str) -> 'Logging':
        return Logging(self.com_object.Add(full_name))

    def remove(self, index: int):
        self.com_object.Remove(index)


class Logging:
    """
    The Logging object represents a Logging Block in the Measurement Setup.
    """
    def __init__(self, logging_com):
        self.com_object = win32com.client.Dispatch(logging_com)

    @property
    def exporter(self) -> 'Exporter':
        return Exporter(self.com_object.Exporter)

    def file_name_options(self):
        raise NotImplementedError("FileNameOptions access is not implemented yet.")

    def filter(self):
        raise NotImplementedError("FileNameOptions access is not implemented yet.")

    @property
    def full_name(self) -> str:
        return self.com_object.FullName

    @full_name.setter
    def full_name(self, fullname: str):
        self.com_object.FullName = fullname

    @property
    def trigger(self) -> "Trigger":
        return Trigger(self.com_object.Trigger)


class Exporter:
    """
    The Exporter object represents an export dialog, as it can be used in CANoe e.g. in a Logging Block in the Measurement Setup.
    """
    def __init__(self, exporter_com):
        self.com_object = win32com.client.Dispatch(exporter_com)

    def destinations(self):
        raise NotImplementedError("Destinations access is not implemented yet.")

    @property
    def filter(self) -> 'Filter':
        return Filter(self.com_object.Filter)

    @property
    def messages(self) -> list['Message']:
        messages_collection = Messages(self.com_object.Symbols)
        messages = []
        for i in range(1, messages_collection.count + 1):
            messages.append(messages_collection.item(i))
        return messages

    def settings(self):
        raise NotImplementedError("FileNameOptions access is not implemented yet.")

    def sources(self):
        raise NotImplementedError("FileNameOptions access is not implemented yet.")

    @property
    def symbols(self) -> list['ExporterSymbol']:
        symbols_collection = ExporterSymbols(self.com_object.Symbols)
        symbols = []
        for i in range(1, symbols_collection.count + 1):
            symbols.append(symbols_collection.item(i))
        return symbols

    def time_section(self):
        raise NotImplementedError("TimeSection access is not implemented yet.")

    def load(self):
        self.com_object.Load()

    def save(self, no_prompt_user: bool = True):
        self.com_object.Save(noPromptUser=no_prompt_user)


class Messages:
    """
    The Messages object represents a collection of messages.
    """
    def __init__(self, messages_com):
        self.com_object = win32com.client.Dispatch(messages_com)

    @property
    def count(self) -> int:
        return int(self.com_object.Count)

    def item(self, index: int) -> 'Message':
        return Message(self.com_object.Item(index))


class Message:
    """
    The Message object represents a single message
    """
    def __init__(self, message_com):
        self.com_object = win32com.client.Dispatch(message_com)

    @property
    def full_name(self) -> str:
        return self.com_object.FullName


class ExporterSymbols:
    """
    The ExporterSymbols object represents a collection of signals, system variables and bus statistics information, found in source files, loaded by the Exporter.
    """
    def __init__(self, symbols_com):
        self.com_object = win32com.client.Dispatch(symbols_com)

    @property
    def count(self) -> int:
        return int(self.com_object.Count)

    def item(self, index: int) -> 'ExporterSymbol':
        return ExporterSymbol(self.com_object.Item(index))


class ExporterSymbol:
    """
    The ExporterSymbol object represents a symbol (signal, system variable or bus statistics information), found in a source file, loaded by the Exporter.
    """
    def __init__(self, message_com):
        self.com_object = win32com.client.Dispatch(message_com)

    @property
    def full_name(self) -> str:
        return self.com_object.FullName


class Filter:
    """
    The Filter object represents a Pass Filter for messages and signals in usage with an exporter.
    """
    def __init__(self, filter_com):
        self.com_object = win32com.client.Dispatch(filter_com)

    @property
    def count(self) -> int:
        return int(self.com_object.Count)

    @property
    def enabled(self) -> bool:
        return self.com_object.Enabled

    @enabled.setter
    def enabled(self, enabled: bool):
        self.com_object.Enabled = enabled

    def item(self, index):
        raise NotImplementedError("Item access is not implemented yet.")

    def add(self, fullname: str):
        self.com_object.Add(fullname)

    def clear(self):
        self.com_object.Clear()

    def remove(self, index: int):
        self.com_object.Remove(index)


class Trigger:
    """
    The Trigger object represents the trigger block that is located before the Logging Block in the Measurement Setup.
    """
    def __init__(self, trigger_com):
        self.com_object = win32com.client.Dispatch(trigger_com)

    @property
    def active(self) -> bool:
        return self.com_object.Active

    @active.setter
    def active(self, value: bool):
        self.com_object.Active = value

    def start(self):
        self.com_object.Start()

    def stop(self):
        self.com_object.Stop()
