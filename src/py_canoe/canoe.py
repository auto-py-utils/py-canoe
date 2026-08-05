import re
import sys
import time
import shutil
import win32com
import pythoncom
from datetime import datetime, timezone
from collections.abc import Sequence
from pathlib import Path
from typing import Union, TYPE_CHECKING, Iterable, Optional, Sequence

if TYPE_CHECKING:
    from py_canoe.core.child_elements.measurement_setup import Logging, ExporterSymbol, Message
    from py_canoe.core.child_elements.test_configurations import TestConfiguration

from py_canoe.core.application import Application
from py_canoe.core.child_elements.bus import Bus
from py_canoe.core.capl import CompileResult
from py_canoe.core.child_elements.test_environment import TestEnvironment
from py_canoe.core.database_utils.db import fetch_database_info
from py_canoe.helpers.bus_type import BusType
from py_canoe.helpers.common import logger, update_logger_file_path, wait
from py_canoe.helpers.exceptions import ConfigurationNotLoadedError
from py_canoe.helpers.vxlapi import ChannelInfo, HwType, VxlDriver, XlBusType


class CANoe:
    def __init__(self, py_canoe_log_dir: str | Path = "", user_capl_functions: Sequence[str] = tuple(), clean_gen_py_cache: bool = False) -> None:
        self.application: Application = None
        try:
            pythoncom.CoInitialize()
            if py_canoe_log_dir:
                update_logger_file_path(logger, py_canoe_log_dir)
            if clean_gen_py_cache:
                self._clean_gen_py_cache()
        except pythoncom.com_error:
            logger.warning("COM already initialized in this thread.")
        except Exception as e:
            logger.error(f"COM init error: {e}")
        finally:
            self.user_capl_functions = user_capl_functions

    def __enter__(self):
        """
        Enter context manager.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit context manager and cleanup resources. Explicitly release resources and uninitialize COM.
        """
        try:
            if self.application is not None:
                pythoncom.CoUninitialize()
        except Exception as e:
            logger.error(f"Error during COM uninitialization: {e}.")
        finally:
            self.application = None

    @staticmethod
    def _clean_gen_py_cache() -> None:
        try:
            # Delete the gen_py cache directory
            gen_py_path = Path(win32com.__gen_path__)
            if gen_py_path.exists() and gen_py_path.is_dir():
                shutil.rmtree(gen_py_path)
                logger.info("Cleared win32com gen_py cache.")
            else:
                logger.info("win32com gen_py cache directory does not exist.")
            # Remove all cached win32com.gen_py modules from sys.modules
            for module_name in list(sys.modules.keys()):
                if re.match(r'win32com\.gen_py\..+', module_name):
                    del sys.modules[module_name]
                    logger.info(f"Removed cached module: {module_name}")
        except Exception as e:
            logger.error(f"Error clearing win32com gen_py cache: {e}")

    def _reset_application(self):
        """Reset application reference without trying to clean up event sinks.

        After a successful quit, the COM server is already shut down, so the event sinks
        are invalid. We just release the Python reference here.
        """
        self.application = None

    def new(self, auto_save=False, prompt_user=False, timeout=5) -> bool:
        """
        Creates a new configuration.

        Args:
            auto_save (bool): Whether to automatically save the configuration. Defaults to False.
            prompt_user (bool): Whether to prompt the user for confirmation. Defaults to False.
            timeout (int): The timeout in seconds for the operation. Defaults to 5.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        self._reset_application()
        self.application = Application()
        return self.application.new(auto_save, prompt_user, timeout)

    def open(self, canoe_cfg: str | Path, visible: bool = True, auto_save: bool = True, prompt_user: bool = False, auto_stop: bool = True, timeout: int = 30) -> bool:
        """
        Loads a configuration.

        Args:
            canoe_cfg (str): The path to the CANoe configuration file.
            visible (bool): Whether to make the CANoe application visible. Defaults to True.
            auto_save (bool): Whether to automatically save the configuration. Defaults to True.
            prompt_user (bool): Whether to prompt the user for confirmation. Defaults to False.
            auto_stop (bool): This argument is deprecated and will be removed in a future version.
            timeout (int): The timeout in seconds for the operation. Defaults to 30.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        self._reset_application()
        self.application = Application()
        self.application.user_capl_functions = self.user_capl_functions
        return self.application.open(canoe_cfg, visible, auto_save, prompt_user, timeout)

    def quit(self, timeout: int = 30) -> bool:
        """
        Quits the application.

        Args:
            timeout (int): The timeout in seconds for the operation. Defaults to 30.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        status = self.application.quit(timeout)
        self._reset_application()
        return status

    def attach_to_active_application(self) -> bool:
        """
        Attach to a active instance of the CANoe application.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        self._reset_application()
        self.application = Application()
        self.application.user_capl_functions = self.user_capl_functions
        return self.application.attach_to_active_application()

    def get_bus_databases_info(self, bus: BusType = BusType.CAN, log_info: bool = False) -> dict:
        """
        Gets the bus databases information.

        Args:
            bus (BusType): The bus type. Defaults to BusType.CAN.
            log_info (bool): Whether to log the databases information. Defaults to False.

        Returns:
            dict: The bus databases information.
        """
        try:
            bus_obj = self.application.bus(bus)
            databases_info = {}
            for db_obj in bus_obj.com_object.Databases:
                db_file = getattr(db_obj, 'FullName', '')
                fetched_db_info = fetch_database_info(db_file)
                ecus = list(fetched_db_info.get('ecus', {}).keys())
                frames = list(fetched_db_info.get('frames', {}).keys())
                frames_signals = list(fetched_db_info.get('frames_signals', {}).keys())
                pdus = list(fetched_db_info.get('pdus', {}).keys())
                pdus_signals = list(fetched_db_info.get('pdus_signals', {}).keys())
                info = {
                    'full_name': getattr(db_obj, 'FullName', ''),
                    'path': getattr(db_obj, 'Path', ''),
                    'name': getattr(db_obj, 'Name', ''),
                    'channel': getattr(db_obj, 'Channel', ''),
                    'com_obj': db_obj,
                    'ecus': ecus,
                    'frames': frames,
                    'frames_signals': frames_signals,
                    'pdus': pdus,
                    'pdus_signals': pdus_signals,
                }
                databases_info[info['name']] = info
            if log_info:
                logger.info(f'{bus.name} bus databases information:')
                for db_name, db_info in databases_info.items():
                    logger.info(f"    {db_name}:")
                    for key, value in db_info.items():
                        logger.info(f"        {key}: {value}")
            return databases_info
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(f"Error retrieving {bus} bus databases information: {e}")
            return {}

    def get_bus_nodes_info(self, bus: BusType = BusType.CAN, log_info: bool = False) -> dict:
        """
        Gets the bus nodes information.

        Args:
            bus (BusType): The bus type. Defaults to BusType.CAN.
            log_info (bool): Whether to log the nodes information. Defaults to False.

        Returns:
            dict: The bus nodes information.
        """
        try:
            bus_obj = self.application.bus(bus)
            nodes_info = {}
            for node_obj in bus_obj.com_object.Nodes:
                info = {
                    'full_name': getattr(node_obj, 'FullName', ''),
                    'path': getattr(node_obj, 'Path', ''),
                    'name': getattr(node_obj, 'Name', ''),
                    'active': getattr(node_obj, 'Active', ''),
                    'com_obj': node_obj,
                }
                nodes_info[info['name']] = info
            if log_info:
                logger.info(f'{bus.name} bus nodes information:')
                for node_name, node_info in nodes_info.items():
                    logger.info(f"    {node_name}:")
                    for key, value in node_info.items():
                        logger.info(f"        {key}: {value}")
            return nodes_info
        except Exception as e:
            logger.error(f"Error retrieving {bus} bus nodes information: {e}")
            return {}

    def get_all_network_names(self) -> list[str]:
        """Returns all network names in the current application."""
        return self.application.networks.get_all_network_names()

    def get_simulation_bus_names(self) -> list[str]:
        """Returns all simulation bus names from the current application."""
        try:
            sim_buses = self.application.configuration.simulation_setup.buses
            bus_names: list[str] = []
            for i in range(1, sim_buses.count + 1):
                sim_bus = sim_buses.item(i)
                if sim_bus.name is not None:
                    bus_names.append(sim_bus.name)
            logger.info(f'simulation buses: {bus_names}')
            return bus_names
        except Exception as e:
            raise ConfigurationNotLoadedError(f"Cannot access simulation buses: {e}") from e

    def get_simulation_database_paths(self) -> list[str]:
        """Returns all simulation database paths from the current application."""
        try:
            sim_buses = self.application.configuration.simulation_setup.buses
            paths: list[str] = []
            for i in range(1, sim_buses.count + 1):
                sim_bus = sim_buses.item(i)
                dbs = sim_bus.databases
                for j in range(1, dbs.count + 1):
                    db = dbs.item(j)
                    if db.full_name is not None:
                        paths.append(db.full_name)
            logger.info(f'simulation database paths: {paths}')
            return paths
        except Exception as e:
            raise ConfigurationNotLoadedError(f"Cannot access simulation databases: {e}") from e

    def get_signal_value(self, bus: BusType, channel: int, message: str, signal: str, raw_value: bool = False, return_timestamp: bool = False) -> Union[int, float, None, tuple]:
        """
        Gets the value of a signal.

        Args:
            bus (BusType): The bus type.
            channel (int): The channel number.
            message (str): The message name.
            signal (str): The signal name.
            raw_value (bool): Whether to get the raw value. Defaults to False.
            return_timestamp (bool): Whether to return the timestamp in timezone utc along with the signal value. Defaults to False.

        Returns:
            Union[int, float, None, tuple]: The signal value or None if not found. If return_timestamp is True, returns a tuple of (signal_value, timestamp).
        """
        signal_value = None
        try:
            signal_obj = self.application.bus(bus).get_signal(channel, message, signal)
            signal_value = signal_obj.raw_value if raw_value else signal_obj.value
            logger.info(f"Signal({signal_obj.full_name}) value = {signal_value}")
        except Exception as e:
            logger.error(f"Error retrieving {bus} bus signal value: {e}")
        if return_timestamp:
            return signal_value, datetime.now(timezone.utc).timestamp()
        return signal_value

    def profile_signal_value(self, bus: BusType, channel: int, message: str, signal: str, duration: float = 1.0, interval: float = 0.0, raw_value: bool = False, max_samples: Optional[int] = None, include_samples: bool = False, include_timestamps: bool = False,) -> dict:
        """Profiles a signal by sampling it repeatedly and returning basic stats.

        This is useful for quickly observing signal stability, typical value range,
        and timing characteristics without storing all the samples in memory.

        Args:
            bus (BusType): The bus type.
            channel (int): The channel number.
            message (str): The message name.
            signal (str): The signal name.
            duration (float): How long to sample the signal (seconds). Defaults to 1.0.
            interval (float): Minimum time to wait between samples (seconds). Defaults to 0.0.
            raw_value (bool): Whether to query the raw value. Defaults to False.
            max_samples (Optional[int]): Stop after collecting this many samples. Defaults to None.
            include_samples (bool): If True, return the list of sampled values.
            include_timestamps (bool): If True, return the list of timestamps for each sample.

        Returns:
            dict: A dictionary with keys:
                - count: number of samples collected
                - duration: actual sampling duration (seconds)
                - min: minimum value (or None if no samples)
                - max: maximum value (or None if no samples)
                - mean: mean value (or None if no samples)
                - std: standard deviation (or None if fewer than 2 samples)
                - samples (optional): list of sampled values
                - timestamps (optional): list of timestamps in UTC seconds
        """
        if duration <= 0:
            return {
                "count": 0,
                "duration": 0.0,
                "min": None,
                "max": None,
                "mean": None,
                "std": None,
                **({"samples": []} if include_samples else {}),
                **({"timestamps": []} if include_timestamps else {}),
            }

        try:
            signal_obj = self.application.bus(bus).get_signal(channel, message, signal)
        except Exception as e:
            logger.error(f"Error retrieving signal object for profiling: {e}")
            return {}

        value_getter = (lambda: signal_obj.raw_value) if raw_value else (lambda: signal_obj.value)

        start = time.perf_counter()
        end_time = start + duration
        count = 0
        mean = 0.0
        m2 = 0.0
        min_value = float("inf")
        max_value = float("-inf")
        samples = [] if include_samples else None
        timestamps = [] if include_timestamps else None
        logger.info(f"Starting signal profiling for {message}::{signal} on {bus} bus for duration {duration}s with interval {interval}s...")
        while True:
            now = time.perf_counter()
            if now >= end_time:
                break
            if max_samples is not None and count >= max_samples:
                break

            value = value_getter()
            # Avoid breaking on missing signals; just skip them
            if value is None:
                if interval > 0:
                    wait(interval)
                continue

            try:
                numeric = float(value)
            except Exception:
                # If value is not numeric, keep the raw value
                numeric = value

            if include_samples:
                samples.append(numeric)
            if include_timestamps:
                timestamps.append(time.time())

            if isinstance(numeric, (int, float)) and not isinstance(numeric, bool):
                count += 1
                if numeric < min_value:
                    min_value = numeric
                if numeric > max_value:
                    max_value = numeric

                # Welford's online algorithm for mean and variance
                delta = numeric - mean
                mean += delta / count
                delta2 = numeric - mean
                m2 += delta * delta2
            else:
                # For non-numeric samples we still count them, but cannot compute stats
                count += 1

            if interval > 0:
                wait(interval)

        duration_actual = time.perf_counter() - start
        variance = m2 / (count - 1) if count > 1 else None
        std = variance**0.5 if variance is not None else None

        profiled_signal = {
            "count": count,
            "duration": duration_actual,
            "min": None if count == 0 else (None if min_value == float("inf") else min_value),
            "max": None if count == 0 else (None if max_value == float("-inf") else max_value),
            "mean": None if count == 0 else mean,
            "std": std,
            **({"samples": samples} if include_samples else {}),
            **({"timestamps": timestamps} if include_timestamps else {}),
        }
        logger.info(
            f"Completed signal profiling for {message}::{signal} on {bus} bus: count={count}, duration={duration_actual:.2f}s, "
            f"min={profiled_signal['min']}, max={profiled_signal['max']}, mean={profiled_signal['mean']}, std={profiled_signal['std']}"
        )
        return profiled_signal

    def set_signal_value(self, bus: BusType, channel: int, message: str, signal: str, value: Union[int, float], raw_value: bool = False) -> bool:
        """
        Sets the value of a signal.

        Args:
            bus (BusType): The bus type.
            channel (int): The channel number.
            message (str): The message name.
            signal (str): The signal name.
            value (Union[int, float]): The value to set.
            raw_value (bool): Whether to set the raw value. Defaults to False.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        try:
            signal_obj = self.application.bus(bus).get_signal(channel, message, signal)
            if raw_value:
                signal_obj.raw_value = int(value)
            else:
                signal_obj.value = value
            logger.info(f"Signal({signal_obj.full_name}) value set to {value}")
            return True
        except Exception as e:
            logger.error(f"Error setting {bus} bus signal value: {e}")
            return False

    def get_signal_full_name(self, bus: BusType, channel: int, message: str, signal: str) -> Union[str, None]:
        """
        Gets the full name of a signal.

        Args:
            bus (BusType): The bus type.
            channel (int): The channel number.
            message (str): The message name.
            signal (str): The signal name.

        Returns:
            Union[str, None]: The full name of the signal or None if not found.
        """
        try:
            signal_obj = self.application.bus(bus).get_signal(channel, message, signal)
            full_name = signal_obj.full_name
            logger.info(f'Signal full name = {full_name}')
            return full_name
        except Exception as e:
            logger.error(f"Error retrieving {bus} bus signal full name: {e}")
            return None

    def check_signal_online(self, bus: BusType, channel: int, message: str, signal: str) -> bool:
        """
        Checks if a signal is online.

        Args:
            bus (BusType): The bus type.
            channel (int): The channel number.
            message (str): The message name.
            signal (str): The signal name.

        Returns:
            bool: True if the signal is online, False otherwise.
        """
        try:
            bus_obj = self.application.bus(bus)
            signal_obj = bus_obj.get_signal(channel, message, signal)
            is_online = signal_obj.is_online
            logger.info(f'Signal({signal_obj.full_name}) is online ?: {is_online} ({bus_obj.VALUE_TABLE_SIGNAL_IS_ONLINE[is_online]})')
            return is_online
        except Exception as e:
            logger.error(f"Error checking {bus} bus signal online status: {e}")
            return False

    def check_signal_state(self, bus: BusType, channel: int, message: str, signal: str) -> int:
        """
        Checks the state of a signal.

        Args:
            bus (BusType): The bus type.
            channel (int): The channel number.
            message (str): The message name.
            signal (str): The signal name.

        Returns:
            int: The state of the signal.
        """
        try:
            bus_obj = self.application.bus(bus)
            signal_obj = bus_obj.get_signal(channel, message, signal)
            state = signal_obj.state
            logger.info(f'Signal({signal_obj.full_name}) state: {state} ({bus_obj.VALUE_TABLE_SIGNAL_STATE[state]})')
            return state
        except Exception as e:
            logger.error(f"Error checking {bus} bus signal state: {e}")
            return -1

    def get_j1939_signal_value(self, bus: BusType, channel: int, message: str, signal: str, source_addr: int, dest_addr: int, raw_value=False, return_timestamp=False) -> Union[float, int, None, tuple]:
        """
        Gets the value of a J1939 signal.

        Args:
            bus (BusType): The bus type.
            channel (int): The channel number.
            message (str): The message name.
            signal (str): The signal name.
            source_addr (int): The source address.
            dest_addr (int): The destination address.
            raw_value (bool): Whether to get the raw value. Defaults to False.
            return_timestamp (bool): Whether to return the timestamp in timezone utc along with the signal value. Defaults to False.

        Returns:
            Union[float, int, None, tuple]: The signal value or None if not found. If return_timestamp is True, returns a tuple of (signal_value, timestamp).
        """
        signal_value = None
        try:
            signal_obj = self.application.bus(bus).get_j1939_signal(channel, message, signal, source_addr, dest_addr)
            signal_value = signal_obj.raw_value if raw_value else signal_obj.value
            logger.info(f'J1939 Signal({signal_obj.full_name}) value = {signal_value}')
        except Exception as e:
            logger.error(f"Error retrieving J1939 bus signal value: {e}")
        if return_timestamp:
            return signal_value, datetime.now(timezone.utc).timestamp()
        return signal_value

    def set_j1939_signal_value(self, bus: BusType, channel: int, message: str, signal: str, source_addr: int, dest_addr: int, value: Union[float, int], raw_value: bool = False) -> bool:
        """
        Sets the value of a J1939 signal.

        Args:
            bus (BusType): The bus type.
            channel (int): The channel number.
            message (str): The message name.
            signal (str): The signal name.
            source_addr (int): The source address.
            dest_addr (int): The destination address.
            value (Union[float, int]): The value to set.
            raw_value (bool): Whether to set the raw value. Defaults to False.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        try:
            signal_obj = self.application.bus(bus).get_j1939_signal(channel, message, signal, source_addr, dest_addr)
            if raw_value:
                signal_obj.raw_value = int(value)
            else:
                signal_obj.value = value
            logger.info(f'J1939 Signal({signal_obj.full_name}) value set to {value}')
            return True
        except Exception as e:
            logger.error(f"Error setting J1939 bus signal value: {e}")
            return False

    def get_j1939_signal_full_name(self, bus: BusType, channel: int, message: str, signal: str, source_addr: int, dest_addr: int) -> Union[str, None]:
        """
        Gets the full name of a J1939 signal.

        Args:
            bus (BusType): The bus type.
            channel (int): The channel number.
            message (str): The message name.
            signal (str): The signal name.
            source_addr (int): The source address.
            dest_addr (int): The destination address.

        Returns:
            Union[str, None]: The full name of the signal or None if not found.
        """
        try:
            signal_obj = self.application.bus(bus).get_j1939_signal(channel, message, signal, source_addr, dest_addr)
            full_name = signal_obj.full_name
            logger.info(f'J1939 Signal full name = {full_name}')
            return full_name
        except Exception as e:
            logger.error(f"Error retrieving J1939 bus signal full name: {e}")
            return None

    def check_j1939_signal_online(self, bus: BusType, channel: int, message: str, signal: str, source_addr: int, dest_addr: int) -> bool:
        """
        Checks if a J1939 signal is online.

        Args:
            bus (BusType): The bus type.
            channel (int): The channel number.
            message (str): The message name.
            signal (str): The signal name.
            source_addr (int): The source address.
            dest_addr (int): The destination address.

        Returns:
            bool: True if the signal is online, False otherwise.
        """
        try:
            bus_obj = self.application.bus(bus)
            signal_obj = bus_obj.get_j1939_signal(channel, message, signal, source_addr, dest_addr)
            is_online = signal_obj.is_online
            logger.info(f'J1939 Signal({signal_obj.full_name}) is online ?: {is_online} ({bus_obj.VALUE_TABLE_SIGNAL_IS_ONLINE[is_online]})')
            return is_online
        except Exception as e:
            logger.error(f"Error checking J1939 bus signal online status: {e}")
            return False

    def check_j1939_signal_state(self, bus: BusType, channel: int, message: str, signal: str, source_addr: int, dest_addr: int) -> int:
        """
        Checks the state of a J1939 signal.

        Args:
            bus (BusType): The bus type.
            channel (int): The channel number.
            message (str): The message name.
            signal (str): The signal name.
            source_addr (int): The source address.
            dest_addr (int): The destination address.

        Returns:
            int: The state of the signal.
        """
        try:
            bus_obj = self.application.bus(bus)
            signal_obj = bus_obj.get_j1939_signal(channel, message, signal, source_addr, dest_addr)
            state = signal_obj.state
            logger.info(f'J1939 Signal({signal_obj.full_name}) state: {state} ({bus_obj.VALUE_TABLE_SIGNAL_STATE[state]})')
            return state
        except Exception as e:
            logger.error(f"Error checking J1939 bus signal state: {e}")
            return -1

    def compile_all_capl_nodes(self, wait_time: Union[int, float] = 5) -> Union[CompileResult, None]:
        """
        Compiles all CAPL nodes in the application.

        Args:
            wait_time (Union[int, float]): The time to wait for the compilation to complete.

        Returns:
            The compilation result or None if an error occurred.
        """
        return self.application.capl.compile(wait_time)

    def call_capl_function(self, name: str, *arguments) -> bool:
        """
        Calls a CAPL function.

        Args:
            name (str): The name of the CAPL function.
            *arguments: The arguments to pass to the CAPL function.

        Returns:
            bool: True if the function call was successful, False otherwise.
        """
        return self.application.capl.call_capl_function(name, *arguments)

    def save_configuration(self) -> bool:
        """
        Saves the current configuration.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.application.configuration.save()

    def save_configuration_as(self, path: str, major: int, minor: int, prompt_user: bool = False, create_dir: bool = True) -> bool:
        """
        Saves the current configuration as a new file.

        Args:
            path (str): The path to save the configuration file.
            major (int): The major version number.
            minor (int): The minor version number.
            prompt_user (bool): Whether to prompt the user for confirmation. Defaults to False.
            create_dir (bool): Whether to create the directory if it doesn't exist. Defaults to True.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.application.configuration.save_as(path, major, minor, prompt_user, create_dir)

    def add_offline_source_log_file(self, absolute_log_file_path: str) -> bool:
        """
        Adds an offline source log file to the configuration.

        Args:
            absolute_log_file_path (str): The absolute path to the log file.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.application.configuration.add_offline_source_log_file(absolute_log_file_path)

    def get_can_bus_statistics(self, channel: int) -> dict:
        """
        Gets the CAN bus statistics.

        Args:
            channel (int): The channel number.

        Returns:
            dict: The CAN bus statistics.
        """
        return self.application.configuration.get_can_bus_statistics(channel)

    def set_replay_block_file(self, block_name: str, recording_file_path: str) -> bool:
        """
        Sets the replay block file.

        Args:
            block_name (str): The name of the replay block.
            recording_file_path (str): The path to the recording file.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.application.configuration.set_replay_block_file(block_name, recording_file_path)

    def control_replay_block(self, block_name: str, start_stop: bool) -> bool:
        """
        Controls the replay block.

        Args:
            block_name (str): The name of the replay block.
            start_stop (bool): True to start the replay block, False to stop it.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.application.configuration.control_replay_block(block_name, start_stop)

    def enable_disable_replay_block(self, block_name: str, enable_disable: bool) -> bool:
        """
        Enables or disables a replay block.

        Args:
            block_name (str): The name of the replay block.
            enable_disable (bool): True to enable the replay block, False to disable it.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.application.configuration.enable_disable_replay_block(block_name, enable_disable)

    def get_test_configurations(self) -> dict[str, 'TestConfiguration']:
        """returns dictionary of test configuration names and its class object."""
        return self.application.configuration.get_test_configurations()

    def get_capl_compilation_result(self) -> dict[str, object]:
        """Returns the current configuration compilation result."""
        return self.application.configuration.get_compilation_result()

    def run_capl_compilation(self) -> bool:
        """Runs compilation for the current configuration."""
        return self.application.configuration.run_compilation()

    def execute_all_test_configurations(self, enable_test_cases: Sequence[str] = (), 
                                       disable_test_cases: Sequence[str] = (), 
                                       match_by: str = "name", 
                                       wait_for_completion: bool = True) -> bool:
        """executes all test configurations available in test setup.

        Args:
            enable_test_cases (Sequence[str]): Patterns of test cases to enable before execution.
            disable_test_cases (Sequence[str]): Patterns of test cases to disable before execution.
            match_by (str): Matching mode for patterns. One of "name", "group", or "fixture". Defaults to "name".
            wait_for_completion (bool): whether to wait for test configuration execution to complete before returning. defaults to True.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.application.configuration.execute_all_test_configurations(enable_test_cases, 
                                                                            disable_test_cases, 
                                                                            match_by,
                                                                            wait_for_completion)

    def stop_all_test_configurations(self) -> bool:
        """stops execution of all test configurations available in test setup.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.application.configuration.stop_all_test_configurations()

    def execute_test_configuration(self, test_configuration_name: str, 
                                   enable_test_cases: Sequence[str] = (), 
                                   disable_test_cases: Sequence[str] = (), 
                                   match_by: str = "name", 
                                   wait_for_completion: bool = True) -> bool:
        """executes a specific test configuration.

        Args:
            test_configuration_name (str): The name of the test configuration to execute.
            enable_test_cases (Sequence[str]): Patterns of test cases to enable before execution.
            disable_test_cases (Sequence[str]): Patterns of test cases to disable before execution.
            match_by (str): Matching mode for patterns. One of "name", "group", or "fixture". Defaults to "name".
            wait_for_completion (bool): Whether to wait for the test configuration execution to complete before returning. Defaults to True.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.application.configuration.execute_test_configuration(test_configuration_name, 
                                                                         enable_test_cases, 
                                                                         disable_test_cases, 
                                                                         match_by,
                                                                         wait_for_completion)

    def get_test_configuration_cases_result(self, test_conf_name: str) -> dict:
        return self.application.configuration.get_test_configurations_cases_result(test_conf_name)
    
    def stop_test_configuration(self, test_configuration_name: str) -> bool:
        """stops execution of a specific test configuration.

        Args:
            test_configuration_name (str): The name of the test configuration to stop.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.application.configuration.stop_test_configuration(test_configuration_name)

    def get_test_environments(self) -> dict:
        """returns dictionary of test environment names and class."""
        return self.application.configuration.get_test_environments()

    def get_test_modules(self, env_name: str) -> dict:
        """returns dictionary of test environment test module names and its class object.

        Args:
            env_name (str): test environment name. avoid duplicate test environment names in CANoe configuration.
        """
        return self.application.configuration.get_test_modules(env_name)

    def execute_test_module(self, test_module_name: str, enable_test_cases: Sequence[str] = (), disable_test_cases: Sequence[str] = (), match_by: str = "name") -> int:
        """use this method to execute test module.

        Args:
            test_module_name (str): test module name. avoid duplicate test module names in CANoe configuration.
            enable_test_cases (Sequence[str]): Patterns of test cases to enable before execution.
                Only matching test cases will be checked. Supports wildcard and regex:
                - Wildcard: ``"*pass*"``, ``"TC_00?"``, ``"TC_[0-3]*"``
                - Regex: ``"(?i)tc_001"``, ``"^SmokeTest_.*"``
                If empty (default), no test cases are explicitly enabled.
            disable_test_cases (Sequence[str]): Patterns of test cases to disable before execution.
                Matching test cases will be unchecked. Takes precedence over enable_test_cases.
                Supports the same wildcard and regex patterns as enable_test_cases.
                If empty (default), no test cases are explicitly disabled.
            match_by (str): Which test case attribute the patterns are matched against.
                Either "name" (default) or "title". Use "title" when your patterns
                describe the test case title rather than its internal name.

        Returns:
            int: test module execution verdict. 0 ='VerdictNotAvailable', 1 = 'VerdictPassed', 2 = 'VerdictFailed',

        Examples:
            >>> # Enable only smoke test cases (matched by name)
            >>> canoe.execute_test_module("MyModule", enable_test_cases=["SmokeTest_*"])

            >>> # Disable slow test cases, enable everything else
            >>> canoe.execute_test_module("MyModule", enable_test_cases=["*"], disable_test_cases=["*slow*", "*stress*"])

            >>> # Use regex to match
            >>> canoe.execute_test_module("MyModule", enable_test_cases=["(?i)^tc_(001|002|003)$"])

            >>> # Match patterns against the test case title instead of name
            >>> canoe.execute_test_module("MyModule", enable_test_cases=["*BLE*"], match_by="title")
        """
        return self.application.configuration.execute_test_module(test_module_name, enable_test_cases, disable_test_cases, match_by=match_by)

    def get_test_module_result(self, test_module_name: str, report_timeout: float = 30.0) -> dict:
        """Get test module execution result including report path, test case
        verdicts, and aggregated statistics.

        Should be called after execute_test_module() to retrieve the results.

        Note: This method does NOT depend on the module's started state. It reads
        the verdict and report information directly from the test module object,
        and waits (up to ``report_timeout`` seconds) for the report-generated
        event if it has not fired yet. All returned data are plain Python objects
        (snapshots), not live COM objects, so they remain valid after the CANoe
        session ends.

        Args:
            test_module_name (str): test module name.
            report_timeout (float): maximum time in seconds to wait for the
                report-generated event before giving up. Defaults to 30.0.

        Returns:
            dict: A dictionary with keys:
                - "test_module" (str): name of the test module
                - "verdict" (int): overall test module verdict (0-5)
                - "verdict_name" (str): human-readable verdict name
                - "report" (dict): report information with keys:
                    - "success" (bool): whether report generation succeeded
                    - "source_full_name" (str): XML report path
                    - "generated_full_name" (str): HTML report path
                - "test_cases" (list[dict]): list of test case snapshots, each
                  with keys: name, title, enabled, verdict, verdict_name
                - "total" (int): total number of test cases
                - "passed" (int): number of passed test cases
                - "failed" (int): number of failed test cases
                - "other" (int): number of test cases with other verdicts
                - "pass_rate" (float): pass rate as a percentage (0.0-100.0)

        Example:
            >>> canoe.execute_test_module("MyModule")
            >>> result = canoe.get_test_module_result("MyModule")
            >>> print(f"Module: {result['test_module']}")
            >>> print(f"Verdict: {result['verdict_name']}")
            >>> print(f"Pass rate: {result['pass_rate']:.1f}%")
            >>> print(f"Passed: {result['passed']}/{result['total']}")
            >>> print(f"Report: {result['report']['generated_full_name']}")
            >>> for tc in result['test_cases']:
            ...     print(f"  {tc['name']}: {tc['verdict_name']}")
        """
        return self.application.configuration.get_test_module_result(test_module_name, report_timeout=report_timeout)

    def stop_test_module(self, test_module_name: str):
        """stops execution of test module.

        Args:
            test_module_name (str): test module name. avoid duplicate test module names in CANoe configuration.
        """
        return self.application.configuration.stop_test_module(test_module_name)

    def execute_all_test_modules_in_test_env(self, env_name: str, enable_test_cases: Sequence[str] = (), disable_test_cases: Sequence[str] = (), match_by: str = "name"):
        """executes all test modules available in test environment.

        Args:
            env_name (str): test environment name. avoid duplicate test environment names in CANoe configuration.
            enable_test_cases (Sequence[str]): Patterns of test cases to enable before
                execution. Forwarded to every test module. Supports wildcard and regex.
                If empty (default), no test cases are explicitly enabled.
            disable_test_cases (Sequence[str]): Patterns of test cases to disable before
                execution. Forwarded to every test module. Takes precedence over
                enable_test_cases. If empty (default), no test cases are disabled.
            match_by (str): Which test case attribute the patterns are matched against.
                Either "name" (default) or "title".
        """
        return self.application.configuration.execute_all_test_modules_in_test_env(
            env_name, enable_test_cases, disable_test_cases, match_by=match_by)

    def stop_all_test_modules_in_test_env(self, env_name: str):
        """stops execution of all test modules available in test environment.

        Args:
            env_name (str): test environment name. avoid duplicate test environment names in CANoe configuration.
        """
        return self.application.configuration.stop_all_test_modules_in_test_env(env_name)

    def execute_all_test_environments(self):
        """executes all test environments available in test setup."""
        return self.application.configuration.execute_all_test_environments()

    def stop_all_test_environments(self):
        """stops execution of all test environments available in test setup."""
        return self.application.configuration.stop_all_test_environments()

    def add_database(self, database_file: str, network: str | int) -> bool:
        """adds database file to a network channel
        
        Args:
            database_file (str): database file to attach. give full file path.
            network (str | int): network name or channel number on which you want to add database.
        """
        return self.application.configuration.add_database(database_file, network)

    def remove_database(self, database_file: str, database_channel: int) -> bool:
        """remove database file from a channel

        Args:
            database_file (str): database file to remove. give full file path.
            database_channel (int): channel name on which you want to remove database.
        """
        return self.application.configuration.remove_database(database_file, database_channel)

    def add_testEnvironments(self, name:str) -> TestEnvironment:
        """
        Add a new Test Environment to TestSetup.

        If you need to create a new test environment, the name field contains the name of the new test environment.
        If you need to load an existing test environment from a file, the name field contains the file path, 
        which can be an absolute path or relative to the current configuration.

        Args:
            name (str): Name or path of the Test Environment
        """
        return self.application.configuration.add_testEnvironments(name)
    
    def add_netWork(self, network_name: str, network_type: BusType = BusType.CAN,
                    sw_channel: int = 1) -> Bus:
        """Adds a new network to the configuration.

        Args:
            network_name: Name of the new network.
            network_type: Bus type. Defaults to BusType.CAN.
            sw_channel: Software channel index (1-based) to assign.
                Defaults to 1.

        Returns:
            The newly added :class:`Bus` object.
        """
        return self.application.configuration.add_netWork(network_name, network_type, sw_channel)

    def add_netWork_with_hardware(self, network_name: str,
                                   network_type: BusType = BusType.CAN,
                                   sw_channel: int = 1,
                                   hw_channel: ChannelInfo | None = None) -> Bus:
        """Add a network and optionally assign a physical hardware channel.

        This combines :meth:`add_netWork` + :meth:`set_hardware_channel`.

        Args:
            network_name: Network name.
            network_type: Bus type.
            sw_channel: Software channel index (1-based).
            hw_channel: Physical hardware channel from
                :meth:`get_hardware_channels`.  Pass *None* to skip
                hardware assignment.

        Returns:
            The newly added :class:`Bus` object.
        """
        bus = self.add_netWork(network_name, network_type, sw_channel)
        if hw_channel is not None:
            # app-channel is 0-based; sw_channel is 1-based
            self.set_hardware_channel(sw_channel - 1, hw_channel, network_type)
        return bus

    def remove_netWork(self, name: str) -> bool:
        """Remove a network by name.

        Note: CANoe requires at least one network.  The last remaining
        network cannot be removed.

        Args:
            name: Network name to remove.

        Returns:
            True if the network was found and removed.
        """
        return self.application.configuration.remove_netWork(name)

    def remove_all_networks(self) -> int:
        """Remove ALL networks from the simulation setup.

        Note: CANoe requires at least one network, so the last remaining
        network is kept.  Returns the number of networks actually removed.
        """
        return self.application.configuration.remove_all_networks()

    def get_network(self,network_name: str = None) -> Bus:
        """Return a specific network by name, or *None* if not found.

        Args:
            network_name: name of the network to retrieve.  If None,
                returns the first network found.
        """
        for bus in self.application.configuration.simulation_setup.buses.item():
            if bus.name == network_name:
                return bus
        return None
    
    def get_channelUsage(self, channel_type:BusType = BusType.CAN) -> list[dict]:
        """returns all available channels of a specific type.

        Args:
            channel_type (BusType): type of the channel (BusType.CAN for CAN, BusType.LIN for LIN, BusType.MOST for MOST, BusType.FlexRay for FlexRay, BusType.J1708 for J1708, BusType.Ethernet for Ethernet, BusType.WLAN for WLAN). Defaults to BusType.CAN.
        """
        return self.application.configuration.general_setup.get_channels_count(channel_type)
    
    def set_channelUsage(self, channel_type:BusType, channel_count:int) -> bool:
        """sets the number of channels of a specific type.

        Args:
            channel_type (BusType): type of the channel (BusType.CAN for CAN, BusType.LIN for LIN, BusType.MOST for MOST, BusType.FlexRay for FlexRay, BusType.J1708 for J1708, BusType.Ethernet for Ethernet, BusType.WLAN for WLAN).
            channel_count (int): number of channels to set.
        """
        self.application.configuration.general_setup.set_channels_count(channel_type, channel_count)

        return self.get_channelUsage(channel_type) == channel_count

    # -- hardware channel mapping (XL Driver) --------------------------------

    _BUS_MAP = {BusType.CAN: XlBusType.CAN, BusType.LIN: XlBusType.LIN,
                 BusType.FlexRay: XlBusType.FLEXRAY, BusType.Ethernet: XlBusType.ETHERNET}

    @staticmethod
    def _to_xl_bus(bus_type: BusType) -> XlBusType:
        if bus_type not in CANoe._BUS_MAP:
            raise ValueError(f"Unsupported BusType for hardware mapping: {bus_type}")
        return CANoe._BUS_MAP[bus_type]

    def get_hardware_channels(self, bus_type: BusType = BusType.CAN) -> list[ChannelInfo]:
        """Return available hardware channels for *bus_type*.

        Args:
            bus_type: CANoe bus type (BusType.CAN, BusType.LIN, etc.).

        Returns:
            List of :class:`ChannelInfo` objects from the XL Driver.
        """
        with VxlDriver() as drv:
            return drv.get_channels(self._to_xl_bus(bus_type))

    def set_hardware_channel(self, app_channel: int, channel: ChannelInfo,
                             bus_type: BusType = BusType.CAN) -> None:
        """Map CANoe logical *app_channel* (0, 1, ...) to a physical hardware
        *channel* returned by :meth:`get_hardware_channels`.

        Example::

            chs = app.get_hardware_channels(BusType.CAN)
            app.set_hardware_channel(0, chs[0], BusType.CAN)
        """
        with VxlDriver() as drv:
            drv.set_appl_config("CANoe", app_channel, channel, bus=self._to_xl_bus(bus_type))

    def clear_hardware_channels(self) -> None:
        """Remove all hardware channel mappings for CANoe."""
        with VxlDriver() as drv:
            drv.unset_all_appl_config("CANoe")

    def get_hardware_config(self, app_channel: int,
                            bus_type: BusType = BusType.CAN) -> ChannelInfo | None:
        """Return the hardware channel mapped to CANoe logical *app_channel*,
        or *None* if not configured."""
        with VxlDriver() as drv:
            return drv.get_appl_config("CANoe", app_channel, self._to_xl_bus(bus_type))

    # -----------------------------------------------------------------------


    def get_logging_blocks(self) -> list['Logging']:
        """Return all available logging blocks."""
        return self.application.configuration.get_logging_blocks()

    def add_logging_block(self, full_name: str) -> 'Logging':
        """adds a new logging block to configuration measurement setup.

        Args:
            full_name (str): full path to log file as "C:/file.(asc|blf|mf4|...)", may have field functions like {IncMeasurement} in the file name.

        Returns:
            Logging: returns Logging object of added logging block.
        """
        return self.application.configuration.add_logging_block(full_name)

    def remove_logging_block(self, index: int) -> None:
        """removes a logging block from configuration measurement setup.

        Args:
            index (int): index of logging block to remove. logging blocks indexing starts from 1 and not 0.
        """
        return self.application.configuration.remove_logging_block(index)

    def load_logs_for_exporter(self, logger_index: int) -> None:
        """Load all source files of exporter and determine symbols/messages.

        Args:
            logger_index (int): indicates logger and its log files
        """
        return self.application.configuration.load_logs_for_exporter(logger_index)

    def get_symbols(self, logger_index: int) -> list['ExporterSymbol']:
        """Return all exporter symbols from given logger."""
        return self.application.configuration.get_symbols(logger_index)

    def get_messages(self, logger_index: int) -> list['Message']:
        """Return all messages from given logger."""
        return self.application.configuration.get_messages(logger_index)

    def add_filters_to_exporter(self, logger_index: int, full_names: 'Iterable'):
        """Add messages and symbols to exporter filter by their full names.

        Args:
            logger_index (int): indicates logger
            full_names (Iterable): full names of messages and symbols
        """
        return self.application.configuration.add_filters_to_exporter(logger_index, full_names)

    def start_export(self, logger_index: int):
        """Starts the export/conversion of exporter.

        Args:
            logger_index (int): indicates logger
        """
        return self.application.configuration.start_export(logger_index)

    def start_stop_online_logging_block(self, full_name: str, start_stop: bool) -> bool:
        """start / stop online measurement setup logging block.

        Args:
            full_name (str): full path to log file as "C:/file.asc"
            start_stop (bool): True to start and False to stop.

        Returns:
            bool: returns true is successfull else false.
        """
        return self.application.configuration.start_stop_online_logging_block(full_name, start_stop)

    def set_configuration_modified(self, modified: bool) -> None:
        """Change status of configuration.

        Args:
            modified (bool): True if configuration is modified, False otherwise.
        """
        return self.application.configuration.set_configuration_modified(modified)

    def get_environment_variable_value(self, env_var_name: str, return_timestamp: bool = False) -> Union[int, float, str, tuple, None]:
        """
        returns a environment variable value.

        Args:
            env_var_name (str): The name of the environment variable. Ex- "float_var"
            return_timestamp (bool): Whether to return the timestamp in timezone utc along with the variable value. Defaults to False.

        Returns:
            Union[int, float, str, tuple, None]: The environment variable value or None if not found. If return_timestamp is True, returns a tuple of (variable_value, timestamp).
        """
        variable_value = self.application.environment.get_environment_variable_value(env_var_name)
        if return_timestamp:
            return variable_value, datetime.now(timezone.utc).timestamp()
        return variable_value

    def set_environment_variable_value(self, env_var_name: str, value: Union[int, float, str, tuple]) -> bool:
        """
        Sets the value of an environment variable.

        Args:
            env_var_name (str): The name of the environment variable. Ex- "speed".
            value (Union[int, float, str, tuple]): variable value. supported CAPL environment variable data types integer, double, string and data.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.application.environment.set_environment_variable_value(env_var_name, value)

    def start_measurement(self, timeout: int = 30) -> bool:
        """
        Starts the measurement.

        Args:
            timeout (int): The timeout in seconds for the operation. Defaults to 30.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.application.measurement.start(timeout)

    def stop_measurement(self, timeout: int = 30) -> bool:
        """
        Stops the measurement.

        Args:
            timeout (int): The timeout in seconds for the operation. Defaults to 30.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.application.measurement.stop(timeout)

    def stop_ex_measurement(self, timeout=30) -> bool:
        """
        Stops the measurement.

        Args:
            timeout (int): The timeout in seconds for the operation. Defaults to 30.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.application.measurement.stop_ex(timeout)

    def reset_measurement(self, timeout=30) -> bool:
        """
        Restarts the measurement if running.

        Args:
            timeout (int): The timeout in seconds for the operation. Defaults to 30.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        if self.application.measurement.running:
            stop_status = self.stop_measurement(timeout)
            start_status = self.start_measurement(timeout)
            return stop_status and start_status
        else:
            logger.warning("Measurement is not running, cannot reset.")
            return False

    def get_measurement_running_status(self) -> bool:
        """
        Gets the running status of the measurement.

        Returns:
            bool: True if the measurement is running, False otherwise.
        """
        return self.application.measurement.running

    def start_measurement_in_animation_mode(self, animation_delay=100, timeout=30) -> bool:
        """
        Starts the measurement in animation mode.

        Args:
            animation_delay (int): The delay in milliseconds for the animation. Defaults to 100.
            timeout (int): The timeout in seconds for the operation. Defaults to 30.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.application.measurement.start_measurement_in_animation_mode(animation_delay, timeout)

    def break_measurement_in_offline_mode(self) -> bool:
        """
        Breaks the measurement in offline mode.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.application.measurement.break_measurement_in_offline_mode()

    def reset_measurement_in_offline_mode(self) -> bool:
        """
        Resets the measurement in offline mode.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.application.measurement.reset_measurement_in_offline_mode()

    def step_measurement_event_in_single_step(self) -> bool:
        """
        Steps the measurement event in single step mode.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.application.measurement.process_measurement_event_in_single_step()

    def get_measurement_index(self) -> int:
        """
        Gets the measurement index.

        Returns:
            int: The measurement index.
        """
        return self.application.measurement.measurement_index

    def set_measurement_index(self, index: int) -> bool:
        """
        Sets the measurement index.

        Args:
            index (int): The measurement index to set.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        self.application.measurement.measurement_index = index
        return True

    def send_diag_request(self, diag_ecu_qualifier_name: str, request: str, request_in_bytes=True, return_sender_name=False, response_in_bytearray=False, timeout: float = 30, poll_s: float = 0.01, **kwargs) -> Union[str, dict]:
        """
        Sends a diagnostic request.

        Args:
            diag_ecu_qualifier_name (str): The diagnostic ECU qualifier name.
            request (str): The diagnostic request.
            request_in_bytes (bool): Whether the request is in bytes.
            return_sender_name (bool): Whether to return the sender name.
            response_in_bytearray (bool): Whether to return the response in bytearray.
            timeout (float): The timeout in seconds for the operation. Defaults to 30.
            poll_s (float): The polling interval in seconds to check for the response. Defaults to 0.01.
            **kwargs (str | int): Key-value pairs used for parametrization of a non-bytes
                request. Accepts symbolic interpretation of parameter value.
        Returns:
            Union[str, dict]: The response from the diagnostic request.

        Example:
            >>> self.send_diag_request("ECU", "WritePropulsionType", False, PropulsionType="BatteryElectric")
        """
        return self.application.networks.send_diag_request(diag_ecu_qualifier_name, request, request_in_bytes, return_sender_name, response_in_bytearray, timeout, poll_s, **kwargs)

    def control_tester_present(self, diag_ecu_qualifier_name: str, value: bool) -> bool:
        """
        Controls the tester present signal.

        Args:
            diag_ecu_qualifier_name (str): The diagnostic ECU qualifier name.
            value (bool): The value to set for the tester present signal.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.application.networks.control_tester_present(diag_ecu_qualifier_name, value)

    def define_system_variable(self, sys_var_name: str, value: Union[int, float, str], read_only: bool = False) -> object:
        """
        Defines a system variable.

        Args:
            sys_var_name (str): The name of the system variable.
            value (Union[int, float, str]): The value of the system variable.
            read_only (bool): Whether the system variable is read-only.

        Returns:
            object: The created system variable object.
        """
        return self.application.system.add_variable(sys_var_name, value, read_only)

    def get_system_variable_value(self, sys_var_name: str, return_symbolic_name: bool = False, return_timestamp: bool = False, enable_events: bool = True) -> Union[int, float, str, None, tuple]:
        """
        Gets the value of a system variable.

        Args:
            sys_var_name (str): The name of the system variable.
            return_symbolic_name (bool): Whether to return the symbolic name.
            return_timestamp (bool): Whether to return the timestamp in timezone utc along with the signal value. Defaults to False.
            enable_events (bool): Whether to enable COM events on the Variable object. Defaults to True.

        Returns:
            Union[int, float, str, None, tuple]: The value of the system variable or None if not found. If return_timestamp is True, returns a tuple of (value, timestamp).
        """
        variable_value = self.application.system.get_variable_value(sys_var_name, return_symbolic_name, enable_events)
        if return_timestamp:
            return variable_value, datetime.now(timezone.utc).timestamp()
        return variable_value

    def get_all_namespace_names(self) -> list[str]:
        """Returns all namespace names from the current application."""
        return self.application.system.get_all_namespace_names()

    def get_all_variables_in_namespace(self, namespace_name: str) -> list[dict]:
        """Returns all variables in the specified namespace."""
        return self.application.system.get_all_variables_in_namespace(namespace_name)

    def set_system_variable_value(self, sys_var_name: str, value: Union[int, float, str]) -> bool:
        """
        Sets the value of a system variable.

        Args:
            sys_var_name (str): The name of the system variable.
            value (Union[int, float, str]): The value to set.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.application.system.set_variable_value(sys_var_name, value)

    def set_system_variable_array_values(self, sys_var_name: str, value: tuple, index: int = 0) -> bool:
        """
        Sets the values of a system variable array.

        Args:
            sys_var_name (str): The name of the system variable.
            value (tuple): The values to set.
            index (int): The index to set the values at.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.application.system.set_variable_array_values(sys_var_name, value, index)

    def ui_activate_desktop(self, name: str) -> bool:
        """
        Activates a desktop by name.

        Args:
            name (str): The name of the desktop to activate.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.application.ui.activate_desktop(name)

    def ui_open_baudrate_dialog(self) -> bool:
        """
        Opens the baudrate dialog.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.application.ui.open_baudrate_dialog()

    def write_text_in_write_window(self, text: str) -> bool:
        """
        Writes text in the write window.

        Args:
            text (str): The text to write.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.application.ui.write.output(text)

    def read_text_from_write_window(self) -> Union[str, None]:
        """
        Reads text from the write window.

        Returns:
            Union[str, None]: The text from the write window or None if not found.
        """
        return self.application.ui.write.text

    def clear_write_window_content(self) -> bool:
        """
        Clears the content of the write window.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.application.ui.write.clear()

    def copy_write_window_content(self) -> bool:
        """
        Copies the content of the write window.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.application.ui.write.copy()

    def enable_write_window_output_file(self, output_file: str, tab_index=None) -> bool:
        """
        Enables the write window output file.

        Args:
            output_file (str): The output file path.
            tab_index (Optional[int]): The tab index to enable the output file for.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.application.ui.write.enable_output_file(output_file, tab_index)

    def disable_write_window_output_file(self, tab_index=None) -> bool:
        """
        Disables the write window output file.

        Args:
            tab_index (Optional[int]): The tab index to disable the output file for.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.application.ui.write.disable_output_file(tab_index)

    def get_canoe_version_info(self) -> dict[str, str | int]:
        """
        Gets the version information of the CANoe application.

        Returns:
            dict: The version information.
        """
        return self.application.version.get_canoe_version_info()
