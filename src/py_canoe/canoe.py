from typing import TYPE_CHECKING, Iterable
if TYPE_CHECKING:
    from py_canoe.core.child_elements.measurement_setup import Logging, ExporterSymbol, Message
    from py_canoe.core.child_elements.test_configurations import TestConfiguration

import re
import sys
import shutil
import win32com
import pythoncom
from datetime import datetime, timezone
from collections.abc import Sequence
from pathlib import Path
from typing import Union

from py_canoe.core.application import Application
from py_canoe.core.capl import CompileResult
from py_canoe.helpers.common import logger, update_logger_file_path


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
            logger.warning("⚠️ COM already initialized in this thread.")
        except Exception as e:
            logger.error(f"❌ COM init error: {e}")
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
            logger.error(f"❌ Error during COM uninitialization: {e}.")
        finally:
            self.application = None

    @staticmethod
    def _clean_gen_py_cache() -> None:
        try:
            # Delete the gen_py cache directory
            gen_py_path = Path(win32com.__gen_path__)
            if gen_py_path.exists() and gen_py_path.is_dir():
                shutil.rmtree(gen_py_path)
                logger.info("🧹 Cleared win32com gen_py cache.")
            else:
                logger.info("ℹ️ win32com gen_py cache directory does not exist.")
            # Remove all cached win32com.gen_py modules from sys.modules
            for module_name in list(sys.modules.keys()):
                if re.match(r'win32com\.gen_py\..+', module_name):
                    del sys.modules[module_name]
                    logger.info(f"🧹 Removed cached module: {module_name}")
        except Exception as e:
            logger.error(f"❌ Error clearing win32com gen_py cache: {e}")

    def _reset_application(self):
        try:
            self.application = None
        except Exception as e:
            logger.error(f"❌ Error during application reset: {e}")

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
            auto_stop (bool): Whether to automatically stop the measurement. Defaults to True.
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

    def get_bus_databases_info(self, bus: str = 'CAN', log_info: bool = False) -> dict:
        """
        Gets the bus databases information.

        Args:
            bus (str): The bus name. Defaults to 'CAN'.
            log_info (bool): Whether to log the databases information. Defaults to False.

        Returns:
            dict: The bus databases information.
        """
        return self.application.bus.get_bus_databases_info(bus, log_info)

    def get_bus_nodes_info(self, bus: str = 'CAN', log_info: bool = False) -> dict:
        """
        Gets the bus nodes information.

        Args:
            bus (str): The bus name. Defaults to 'CAN'.
            log_info (bool): Whether to log the nodes information. Defaults to False.

        Returns:
            dict: The bus nodes information.
        """
        return self.application.bus.get_bus_nodes_info(bus, log_info)

    def get_signal_value(self, bus: str, channel: int, message: str, signal: str, raw_value: bool = False, return_timestamp: bool = False) -> Union[int, float, None, tuple]:
        """
        Gets the value of a signal.

        Args:
            bus (str): The bus name.
            channel (int): The channel number.
            message (str): The message name.
            signal (str): The signal name.
            raw_value (bool): Whether to get the raw value. Defaults to False.
            return_timestamp (bool): Whether to return the timestamp in timezone utc along with the signal value. Defaults to False.

        Returns:
            Union[int, float, None, tuple]: The signal value or None if not found. If return_timestamp is True, returns a tuple of (signal_value, timestamp).
        """
        signal_value = self.application.bus.get_signal_value(bus, channel, message, signal, raw_value)
        if return_timestamp:
            return signal_value, datetime.now(timezone.utc).timestamp()
        return signal_value

    def profile_signal_value(
        self,
        bus: str,
        channel: int,
        message: str,
        signal: str,
        duration: float = 1.0,
        interval: float = 0.0,
        raw_value: bool = False,
        max_samples: Optional[int] = None,
        include_samples: bool = False,
        include_timestamps: bool = False,
    ) -> dict:
        """Profiles a signal by sampling it repeatedly and returning basic stats.

        This is useful for quickly observing signal stability, typical value range,
        and timing characteristics without storing all the samples in memory.

        Args:
            bus (str): The bus name.
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
        return self.application.bus.profile_signal_value(bus, channel, message, signal, duration, interval, raw_value, max_samples, include_samples, include_timestamps)

    def set_signal_value(self, bus: str, channel: int, message: str, signal: str, value: Union[int, float], raw_value: bool = False) -> bool:
        """
        Sets the value of a signal.

        Args:
            bus (str): The bus name.
            channel (int): The channel number.
            message (str): The message name.
            signal (str): The signal name.
            value (Union[int, float]): The value to set.
            raw_value (bool): Whether to set the raw value. Defaults to False.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.application.bus.set_signal_value(bus, channel, message, signal, value, raw_value)

    def get_signal_full_name(self, bus: str, channel: int, message: str, signal: str) -> Union[str, None]:
        """
        Gets the full name of a signal.

        Args:
            bus (str): The bus name.
            channel (int): The channel number.
            message (str): The message name.
            signal (str): The signal name.

        Returns:
            Union[str, None]: The full name of the signal or None if not found.
        """
        return self.application.bus.get_signal_full_name(bus, channel, message, signal)

    def check_signal_online(self, bus: str, channel: int, message: str, signal: str) -> bool:
        """
        Checks if a signal is online.

        Args:
            bus (str): The bus name.
            channel (int): The channel number.
            message (str): The message name.
            signal (str): The signal name.

        Returns:
            bool: True if the signal is online, False otherwise.
        """
        return self.application.bus.check_signal_online(bus, channel, message, signal)

    def check_signal_state(self, bus: str, channel: int, message: str, signal: str) -> int:
        """
        Checks the state of a signal.

        Args:
            bus (str): The bus name.
            channel (int): The channel number.
            message (str): The message name.
            signal (str): The signal name.

        Returns:
            int: The state of the signal.
        """
        return self.application.bus.check_signal_state(bus, channel, message, signal)

    def get_j1939_signal_value(self, bus: str, channel: int, message: str, signal: str, source_addr: int, dest_addr: int, raw_value=False, return_timestamp=False) -> Union[float, int, None, tuple]:
        """
        Gets the value of a J1939 signal.

        Args:
            bus (str): The bus name.
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
        signal_value = self.application.bus.get_j1939_signal_value(bus, channel, message, signal, source_addr, dest_addr, raw_value)
        if return_timestamp:
            return signal_value, datetime.now(timezone.utc).timestamp()
        return signal_value

    def set_j1939_signal_value(self, bus: str, channel: int, message: str, signal: str, source_addr: int, dest_addr: int, value: Union[float, int], raw_value: bool = False) -> bool:
        """
        Sets the value of a J1939 signal.

        Args:
            bus (str): The bus name.
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
        return self.application.bus.set_j1939_signal_value(bus, channel, message, signal, source_addr, dest_addr, value, raw_value)

    def get_j1939_signal_full_name(self, bus: str, channel: int, message: str, signal: str, source_addr: int, dest_addr: int) -> Union[str, None]:
        """
        Gets the full name of a J1939 signal.

        Args:
            bus (str): The bus name.
            channel (int): The channel number.
            message (str): The message name.
            signal (str): The signal name.
            source_addr (int): The source address.
            dest_addr (int): The destination address.

        Returns:
            Union[str, None]: The full name of the signal or None if not found.
        """
        return self.application.bus.get_j1939_signal_full_name(bus, channel, message, signal, source_addr, dest_addr)

    def check_j1939_signal_online(self, bus: str, channel: int, message: str, signal: str, source_addr: int, dest_addr: int) -> bool:
        """
        Checks if a J1939 signal is online.

        Args:
            bus (str): The bus name.
            channel (int): The channel number.
            message (str): The message name.
            signal (str): The signal name.
            source_addr (int): The source address.
            dest_addr (int): The destination address.

        Returns:
            bool: True if the signal is online, False otherwise.
        """
        return self.application.bus.check_j1939_signal_online(bus, channel, message, signal, source_addr, dest_addr)

    def check_j1939_signal_state(self, bus: str, channel: int, message: str, signal: str, source_addr: int, dest_addr: int) -> int:
        """
        Checks the state of a J1939 signal.

        Args:
            bus (str): The bus name.
            channel (int): The channel number.
            message (str): The message name.
            signal (str): The signal name.
            source_addr (int): The source address.
            dest_addr (int): The destination address.

        Returns:
            int: The state of the signal.
        """
        return self.application.bus.check_j1939_signal_state(bus, channel, message, signal, source_addr, dest_addr)

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

    def execute_all_test_configurations(self, wait_for_completion: bool = True) -> bool:
        """executes all test configurations available in test setup.

        Args:
            wait_for_completion (bool): whether to wait for test configuration execution to complete before returning. defaults to True.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.application.configuration.execute_all_test_configurations(wait_for_completion)

    def stop_all_test_configurations(self) -> bool:
        """stops execution of all test configurations available in test setup.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.application.configuration.stop_all_test_configurations()

    def execute_test_configuration(self, test_configuration_name: str, wait_for_completion: bool = True) -> bool:
        """executes a specific test configuration.

        Args:
            test_configuration_name (str): The name of the test configuration to execute.
            wait_for_completion (bool): Whether to wait for the test configuration execution to complete before returning. Defaults to True.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.application.configuration.execute_test_configuration(test_configuration_name, wait_for_completion)

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

    def execute_test_module(self, test_module_name: str) -> int:
        """use this method to execute test module.

        Args:
            test_module_name (str): test module name. avoid duplicate test module names in CANoe configuration.

        Returns:
            int: test module execution verdict. 0 ='VerdictNotAvailable', 1 = 'VerdictPassed', 2 = 'VerdictFailed',
        """
        return self.application.configuration.execute_test_module(test_module_name)

    def stop_test_module(self, test_module_name: str):
        """stops execution of test module.

        Args:
            test_module_name (str): test module name. avoid duplicate test module names in CANoe configuration.
        """
        return self.application.configuration.stop_test_module(test_module_name)

    def execute_all_test_modules_in_test_env(self, env_name: str):
        """executes all test modules available in test environment.

        Args:
            env_name (str): test environment name. avoid duplicate test environment names in CANoe configuration.
        """
        return self.application.configuration.execute_all_test_modules_in_test_env(env_name)

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

    def add_database(self, database_file: str, database_channel: int, database_network: Union[str, None]=None) -> bool:
        """adds database file to a network channel

        Args:
            database_file (str): database file to attach. give full file path.
            database_network (str): network name on which you want to add this database.
            database_channel (int): channel name on which you want to add this database.
        """
        return self.application.configuration.add_database(database_file, database_channel, database_network)

    def remove_database(self, database_file: str, database_channel: int) -> bool:
        """remove database file from a channel

        Args:
            database_file (str): database file to remove. give full file path.
            database_channel (int): channel name on which you want to remove database.
        """
        return self.application.configuration.remove_database(database_file, database_channel)

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
            logger.warning("⚠️ Measurement is not running, cannot reset.")
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

    def send_diag_request(self, diag_ecu_qualifier_name: str, request: str, request_in_bytes=True, return_sender_name=False, response_in_bytearray=False) -> Union[str, dict]:
        """
        Sends a diagnostic request.

        Args:
            diag_ecu_qualifier_name (str): The diagnostic ECU qualifier name.
            request (str): The diagnostic request.
            request_in_bytes (bool): Whether the request is in bytes.
            return_sender_name (bool): Whether to return the sender name.
            response_in_bytearray (bool): Whether to return the response in bytearray.

        Returns:
            Union[str, dict]: The response from the diagnostic request.
        """
        return self.application.networks.send_diag_request(diag_ecu_qualifier_name, request, request_in_bytes, return_sender_name, response_in_bytearray)

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

    def get_system_variable_value(self, sys_var_name: str, return_symbolic_name: bool = False, return_timestamp: bool = False) -> Union[int, float, str, None, tuple]:
        """
        Gets the value of a system variable.

        Args:
            sys_var_name (str): The name of the system variable.
            return_symbolic_name (bool): Whether to return the symbolic name.
            return_timestamp (bool): Whether to return the timestamp in timezone utc along with the signal value. Defaults to False.

        Returns:
            Union[int, float, str, None, tuple]: The value of the system variable or None if not found. If return_timestamp is True, returns a tuple of (value, timestamp).
        """
        variable_value = self.application.system.get_variable_value(sys_var_name, return_symbolic_name)
        if return_timestamp:
            return variable_value, datetime.now(timezone.utc).timestamp()
        return variable_value

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
