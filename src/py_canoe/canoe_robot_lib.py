# ---------------------------------------------------------------------------
# THIS FILE IS AUTO-GENERATED - DO NOT EDIT MANUALLY
# Generated: 2026-07-15T17:23:31.341774+00:00
# py-canoe package version: 26.3.3
# To update this file, run the generator: python -m py_canoe.helpers.gen_canoe_robot_lib
# ---------------------------------------------------------------------------

from typing import Iterable, Optional, Sequence, TYPE_CHECKING, Union
if TYPE_CHECKING:
    from py_canoe.core.child_elements.measurement_setup import Logging, ExporterSymbol, Message
    from py_canoe.core.child_elements.test_configurations import TestConfiguration
from collections.abc import Sequence
from pathlib import Path
from py_canoe.core.capl import CompileResult

from py_canoe.canoe import CANoe


class CanoeRobotLib:
    """Robot Framework library wrapper around CANoe."""

    def __init__(self, py_canoe_log_dir: str | Path='', user_capl_functions: Sequence[str]=tuple(), clean_gen_py_cache: bool=False):
        self._source = CANoe(py_canoe_log_dir, user_capl_functions, clean_gen_py_cache)

    def canoe_new(self, auto_save=False, prompt_user=False, timeout=5) -> bool:
        """
        Creates a new configuration.
        
        Args:
            auto_save (bool): Whether to automatically save the configuration. Defaults to False.
            prompt_user (bool): Whether to prompt the user for confirmation. Defaults to False.
            timeout (int): The timeout in seconds for the operation. Defaults to 5.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self._source.new(auto_save, prompt_user, timeout)

    def canoe_open(self, canoe_cfg: str | Path, visible: bool=True, auto_save: bool=True, prompt_user: bool=False, auto_stop: bool=True, timeout: int=30) -> bool:
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
        return self._source.open(canoe_cfg, visible, auto_save, prompt_user, auto_stop, timeout)

    def canoe_quit(self, timeout: int=30) -> bool:
        """
        Quits the application.
        
        Args:
            timeout (int): The timeout in seconds for the operation. Defaults to 30.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self._source.quit(timeout)

    def canoe_attach_to_active_application(self) -> bool:
        """
        Attach to a active instance of the CANoe application.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self._source.attach_to_active_application()

    def canoe_get_bus_databases_info(self, bus: str='CAN', log_info: bool=False) -> dict:
        """
        Gets the bus databases information.
        
        Args:
            bus (str): The bus name. Defaults to 'CAN'.
            log_info (bool): Whether to log the databases information. Defaults to False.
        
        Returns:
            dict: The bus databases information.
        """
        return self._source.get_bus_databases_info(bus, log_info)

    def canoe_get_bus_nodes_info(self, bus: str='CAN', log_info: bool=False) -> dict:
        """
        Gets the bus nodes information.
        
        Args:
            bus (str): The bus name. Defaults to 'CAN'.
            log_info (bool): Whether to log the nodes information. Defaults to False.
        
        Returns:
            dict: The bus nodes information.
        """
        return self._source.get_bus_nodes_info(bus, log_info)

    def canoe_get_all_network_names(self) -> list[str]:
        """Returns all network names in the current application."""
        return self._source.get_all_network_names()

    def canoe_get_simulation_bus_names(self) -> list[str]:
        """Returns all simulation bus names from the current application."""
        return self._source.get_simulation_bus_names()

    def canoe_get_simulation_database_paths(self) -> list[str]:
        """Returns all simulation database paths from the current application."""
        return self._source.get_simulation_database_paths()

    def canoe_get_signal_value(self, bus: str, channel: int, message: str, signal: str, raw_value: bool=False, return_timestamp: bool=False) -> Union[int, float, None, tuple]:
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
        return self._source.get_signal_value(bus, channel, message, signal, raw_value, return_timestamp)

    def canoe_profile_signal_value(self, bus: str, channel: int, message: str, signal: str, duration: float=1.0, interval: float=0.0, raw_value: bool=False, max_samples: Optional[int]=None, include_samples: bool=False, include_timestamps: bool=False) -> dict:
        """
        Profiles a signal by sampling it repeatedly and returning basic stats.
        
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
        return self._source.profile_signal_value(bus, channel, message, signal, duration, interval, raw_value, max_samples, include_samples, include_timestamps)

    def canoe_set_signal_value(self, bus: str, channel: int, message: str, signal: str, value: Union[int, float], raw_value: bool=False) -> bool:
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
        return self._source.set_signal_value(bus, channel, message, signal, value, raw_value)

    def canoe_get_signal_full_name(self, bus: str, channel: int, message: str, signal: str) -> Union[str, None]:
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
        return self._source.get_signal_full_name(bus, channel, message, signal)

    def canoe_check_signal_online(self, bus: str, channel: int, message: str, signal: str) -> bool:
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
        return self._source.check_signal_online(bus, channel, message, signal)

    def canoe_check_signal_state(self, bus: str, channel: int, message: str, signal: str) -> int:
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
        return self._source.check_signal_state(bus, channel, message, signal)

    def canoe_get_j1939_signal_value(self, bus: str, channel: int, message: str, signal: str, source_addr: int, dest_addr: int, raw_value=False, return_timestamp=False) -> Union[float, int, None, tuple]:
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
        return self._source.get_j1939_signal_value(bus, channel, message, signal, source_addr, dest_addr, raw_value, return_timestamp)

    def canoe_set_j1939_signal_value(self, bus: str, channel: int, message: str, signal: str, source_addr: int, dest_addr: int, value: Union[float, int], raw_value: bool=False) -> bool:
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
        return self._source.set_j1939_signal_value(bus, channel, message, signal, source_addr, dest_addr, value, raw_value)

    def canoe_get_j1939_signal_full_name(self, bus: str, channel: int, message: str, signal: str, source_addr: int, dest_addr: int) -> Union[str, None]:
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
        return self._source.get_j1939_signal_full_name(bus, channel, message, signal, source_addr, dest_addr)

    def canoe_check_j1939_signal_online(self, bus: str, channel: int, message: str, signal: str, source_addr: int, dest_addr: int) -> bool:
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
        return self._source.check_j1939_signal_online(bus, channel, message, signal, source_addr, dest_addr)

    def canoe_check_j1939_signal_state(self, bus: str, channel: int, message: str, signal: str, source_addr: int, dest_addr: int) -> int:
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
        return self._source.check_j1939_signal_state(bus, channel, message, signal, source_addr, dest_addr)

    def canoe_compile_all_capl_nodes(self, wait_time: Union[int, float]=5) -> Union[CompileResult, None]:
        """
        Compiles all CAPL nodes in the application.
        
        Args:
            wait_time (Union[int, float]): The time to wait for the compilation to complete.
        
        Returns:
            The compilation result or None if an error occurred.
        """
        return self._source.compile_all_capl_nodes(wait_time)

    def canoe_call_capl_function(self, name: str, *arguments) -> bool:
        """
        Calls a CAPL function.
        
        Args:
            name (str): The name of the CAPL function.
            *arguments: The arguments to pass to the CAPL function.
        
        Returns:
            bool: True if the function call was successful, False otherwise.
        """
        return self._source.call_capl_function(name, *arguments)

    def canoe_save_configuration(self) -> bool:
        """
        Saves the current configuration.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self._source.save_configuration()

    def canoe_save_configuration_as(self, path: str, major: int, minor: int, prompt_user: bool=False, create_dir: bool=True) -> bool:
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
        return self._source.save_configuration_as(path, major, minor, prompt_user, create_dir)

    def canoe_add_offline_source_log_file(self, absolute_log_file_path: str) -> bool:
        """
        Adds an offline source log file to the configuration.
        
        Args:
            absolute_log_file_path (str): The absolute path to the log file.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self._source.add_offline_source_log_file(absolute_log_file_path)

    def canoe_get_can_bus_statistics(self, channel: int) -> dict:
        """
        Gets the CAN bus statistics.
        
        Args:
            channel (int): The channel number.
        
        Returns:
            dict: The CAN bus statistics.
        """
        return self._source.get_can_bus_statistics(channel)

    def canoe_set_replay_block_file(self, block_name: str, recording_file_path: str) -> bool:
        """
        Sets the replay block file.
        
        Args:
            block_name (str): The name of the replay block.
            recording_file_path (str): The path to the recording file.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self._source.set_replay_block_file(block_name, recording_file_path)

    def canoe_control_replay_block(self, block_name: str, start_stop: bool) -> bool:
        """
        Controls the replay block.
        
        Args:
            block_name (str): The name of the replay block.
            start_stop (bool): True to start the replay block, False to stop it.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self._source.control_replay_block(block_name, start_stop)

    def canoe_enable_disable_replay_block(self, block_name: str, enable_disable: bool) -> bool:
        """
        Enables or disables a replay block.
        
        Args:
            block_name (str): The name of the replay block.
            enable_disable (bool): True to enable the replay block, False to disable it.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self._source.enable_disable_replay_block(block_name, enable_disable)

    def canoe_get_test_configurations(self) -> dict[str, 'TestConfiguration']:
        """returns dictionary of test configuration names and its class object."""
        return self._source.get_test_configurations()

    def canoe_get_capl_compilation_result(self) -> dict[str, object]:
        """Returns the current configuration compilation result."""
        return self._source.get_capl_compilation_result()

    def canoe_run_capl_compilation(self) -> bool:
        """Runs compilation for the current configuration."""
        return self._source.run_capl_compilation()

    def canoe_execute_all_test_configurations(self, enable_test_cases: Sequence[str]=(), disable_test_cases: Sequence[str]=(), match_by: str='name', wait_for_completion: bool=True) -> bool:
        """
        executes all test configurations available in test setup.
        
        Args:
            enable_test_cases (Sequence[str]): Patterns of test cases to enable before execution.
            disable_test_cases (Sequence[str]): Patterns of test cases to disable before execution.
            match_by (str): Matching mode for patterns. One of "name", "group", or "fixture". Defaults to "name".
            wait_for_completion (bool): whether to wait for test configuration execution to complete before returning. defaults to True.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self._source.execute_all_test_configurations(enable_test_cases, disable_test_cases, match_by, wait_for_completion)

    def canoe_stop_all_test_configurations(self) -> bool:
        """
        stops execution of all test configurations available in test setup.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self._source.stop_all_test_configurations()

    def canoe_execute_test_configuration(self, test_configuration_name: str, enable_test_cases: Sequence[str]=(), disable_test_cases: Sequence[str]=(), match_by: str='name', wait_for_completion: bool=True) -> bool:
        """
        executes a specific test configuration.
        
        Args:
            test_configuration_name (str): The name of the test configuration to execute.
            enable_test_cases (Sequence[str]): Patterns of test cases to enable before execution.
            disable_test_cases (Sequence[str]): Patterns of test cases to disable before execution.
            match_by (str): Matching mode for patterns. One of "name", "group", or "fixture". Defaults to "name".
            wait_for_completion (bool): Whether to wait for the test configuration execution to complete before returning. Defaults to True.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self._source.execute_test_configuration(test_configuration_name, enable_test_cases, disable_test_cases, match_by, wait_for_completion)

    def canoe_stop_test_configuration(self, test_configuration_name: str) -> bool:
        """
        stops execution of a specific test configuration.
        
        Args:
            test_configuration_name (str): The name of the test configuration to stop.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self._source.stop_test_configuration(test_configuration_name)

    def canoe_get_test_environments(self) -> dict:
        """returns dictionary of test environment names and class."""
        return self._source.get_test_environments()

    def canoe_get_test_modules(self, env_name: str) -> dict:
        """
        returns dictionary of test environment test module names and its class object.
        
        Args:
            env_name (str): test environment name. avoid duplicate test environment names in CANoe configuration.
        """
        return self._source.get_test_modules(env_name)

    def canoe_execute_test_module(self, test_module_name: str, enable_test_cases: Sequence[str]=(), disable_test_cases: Sequence[str]=(), match_by: str='name') -> int:
        """
        use this method to execute test module.
        
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
        return self._source.execute_test_module(test_module_name, enable_test_cases, disable_test_cases, match_by)

    def canoe_get_test_module_result(self, test_module_name: str) -> dict:
        """
        Get test module execution result including report path and test case verdicts.
        
        Should be called after execute_test_module() to retrieve the results.
        
        Args:
            test_module_name (str): test module name.
        
        Returns:
            dict: A dictionary with keys:
                - "verdict" (int): overall test module verdict (0-5)
                - "verdict_name" (str): human-readable verdict name
                - "report" (dict): report information with keys:
                    - "success" (bool): whether report generation succeeded
                    - "source_full_name" (str): XML report path
                    - "generated_full_name" (str): HTML report path
                - "test_cases" (dict[str, dict]): mapping of test case names to dicts
                  with keys "name", "enabled", "verdict", "verdict_name", "title"
        
        Example:
            >>> canoe.execute_test_module("MyModule")
            >>> result = canoe.get_test_module_result("MyModule")
            >>> print(f"Verdict: {result['verdict_name']}")
            >>> print(f"Report: {result['report']['generated_full_name']}")
            >>> for name, tc in result['test_cases'].items():
            ...     print(f"  {name}: {tc['verdict_name']}")
        """
        return self._source.get_test_module_result(test_module_name)

    def canoe_stop_test_module(self, test_module_name: str):
        """
        stops execution of test module.
        
        Args:
            test_module_name (str): test module name. avoid duplicate test module names in CANoe configuration.
        """
        return self._source.stop_test_module(test_module_name)

    def canoe_execute_all_test_modules_in_test_env(self, env_name: str, enable_test_cases: Sequence[str]=(), disable_test_cases: Sequence[str]=(), match_by: str='name'):
        """
        executes all test modules available in test environment.
        
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
        return self._source.execute_all_test_modules_in_test_env(env_name, enable_test_cases, disable_test_cases, match_by)

    def canoe_stop_all_test_modules_in_test_env(self, env_name: str):
        """
        stops execution of all test modules available in test environment.
        
        Args:
            env_name (str): test environment name. avoid duplicate test environment names in CANoe configuration.
        """
        return self._source.stop_all_test_modules_in_test_env(env_name)

    def canoe_execute_all_test_environments(self):
        """executes all test environments available in test setup."""
        return self._source.execute_all_test_environments()

    def canoe_stop_all_test_environments(self):
        """stops execution of all test environments available in test setup."""
        return self._source.stop_all_test_environments()

    def canoe_add_database(self, database_file: str, database_channel: int, database_network: Union[str, None]=None) -> bool:
        """
        adds database file to a network channel
        
        Args:
            database_file (str): database file to attach. give full file path.
            database_network (str): network name on which you want to add this database.
            database_channel (int): channel name on which you want to add this database.
        """
        return self._source.add_database(database_file, database_channel, database_network)

    def canoe_remove_database(self, database_file: str, database_channel: int) -> bool:
        """
        remove database file from a channel
        
        Args:
            database_file (str): database file to remove. give full file path.
            database_channel (int): channel name on which you want to remove database.
        """
        return self._source.remove_database(database_file, database_channel)

    def canoe_get_logging_blocks(self) -> list['Logging']:
        """Return all available logging blocks."""
        return self._source.get_logging_blocks()

    def canoe_add_logging_block(self, full_name: str) -> 'Logging':
        """
        adds a new logging block to configuration measurement setup.
        
        Args:
            full_name (str): full path to log file as "C:/file.(asc|blf|mf4|...)", may have field functions like {IncMeasurement} in the file name.
        
        Returns:
            Logging: returns Logging object of added logging block.
        """
        return self._source.add_logging_block(full_name)

    def canoe_remove_logging_block(self, index: int) -> None:
        """
        removes a logging block from configuration measurement setup.
        
        Args:
            index (int): index of logging block to remove. logging blocks indexing starts from 1 and not 0.
        """
        return self._source.remove_logging_block(index)

    def canoe_load_logs_for_exporter(self, logger_index: int) -> None:
        """
        Load all source files of exporter and determine symbols/messages.
        
        Args:
            logger_index (int): indicates logger and its log files
        """
        return self._source.load_logs_for_exporter(logger_index)

    def canoe_get_symbols(self, logger_index: int) -> list['ExporterSymbol']:
        """Return all exporter symbols from given logger."""
        return self._source.get_symbols(logger_index)

    def canoe_get_messages(self, logger_index: int) -> list['Message']:
        """Return all messages from given logger."""
        return self._source.get_messages(logger_index)

    def canoe_add_filters_to_exporter(self, logger_index: int, full_names: 'Iterable'):
        """
        Add messages and symbols to exporter filter by their full names.
        
        Args:
            logger_index (int): indicates logger
            full_names (Iterable): full names of messages and symbols
        """
        return self._source.add_filters_to_exporter(logger_index, full_names)

    def canoe_start_export(self, logger_index: int):
        """
        Starts the export/conversion of exporter.
        
        Args:
            logger_index (int): indicates logger
        """
        return self._source.start_export(logger_index)

    def canoe_start_stop_online_logging_block(self, full_name: str, start_stop: bool) -> bool:
        """
        start / stop online measurement setup logging block.
        
        Args:
            full_name (str): full path to log file as "C:/file.asc"
            start_stop (bool): True to start and False to stop.
        
        Returns:
            bool: returns true is successfull else false.
        """
        return self._source.start_stop_online_logging_block(full_name, start_stop)

    def canoe_set_configuration_modified(self, modified: bool) -> None:
        """
        Change status of configuration.
        
        Args:
            modified (bool): True if configuration is modified, False otherwise.
        """
        return self._source.set_configuration_modified(modified)

    def canoe_get_environment_variable_value(self, env_var_name: str, return_timestamp: bool=False) -> Union[int, float, str, tuple, None]:
        """
        returns a environment variable value.
        
        Args:
            env_var_name (str): The name of the environment variable. Ex- "float_var"
            return_timestamp (bool): Whether to return the timestamp in timezone utc along with the variable value. Defaults to False.
        
        Returns:
            Union[int, float, str, tuple, None]: The environment variable value or None if not found. If return_timestamp is True, returns a tuple of (variable_value, timestamp).
        """
        return self._source.get_environment_variable_value(env_var_name, return_timestamp)

    def canoe_set_environment_variable_value(self, env_var_name: str, value: Union[int, float, str, tuple]) -> bool:
        """
        Sets the value of an environment variable.
        
        Args:
            env_var_name (str): The name of the environment variable. Ex- "speed".
            value (Union[int, float, str, tuple]): variable value. supported CAPL environment variable data types integer, double, string and data.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self._source.set_environment_variable_value(env_var_name, value)

    def canoe_start_measurement(self, timeout: int=30) -> bool:
        """
        Starts the measurement.
        
        Args:
            timeout (int): The timeout in seconds for the operation. Defaults to 30.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self._source.start_measurement(timeout)

    def canoe_stop_measurement(self, timeout: int=30) -> bool:
        """
        Stops the measurement.
        
        Args:
            timeout (int): The timeout in seconds for the operation. Defaults to 30.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self._source.stop_measurement(timeout)

    def canoe_stop_ex_measurement(self, timeout=30) -> bool:
        """
        Stops the measurement.
        
        Args:
            timeout (int): The timeout in seconds for the operation. Defaults to 30.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self._source.stop_ex_measurement(timeout)

    def canoe_reset_measurement(self, timeout=30) -> bool:
        """
        Restarts the measurement if running.
        
        Args:
            timeout (int): The timeout in seconds for the operation. Defaults to 30.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self._source.reset_measurement(timeout)

    def canoe_get_measurement_running_status(self) -> bool:
        """
        Gets the running status of the measurement.
        
        Returns:
            bool: True if the measurement is running, False otherwise.
        """
        return self._source.get_measurement_running_status()

    def canoe_start_measurement_in_animation_mode(self, animation_delay=100, timeout=30) -> bool:
        """
        Starts the measurement in animation mode.
        
        Args:
            animation_delay (int): The delay in milliseconds for the animation. Defaults to 100.
            timeout (int): The timeout in seconds for the operation. Defaults to 30.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self._source.start_measurement_in_animation_mode(animation_delay, timeout)

    def canoe_break_measurement_in_offline_mode(self) -> bool:
        """
        Breaks the measurement in offline mode.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self._source.break_measurement_in_offline_mode()

    def canoe_reset_measurement_in_offline_mode(self) -> bool:
        """
        Resets the measurement in offline mode.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self._source.reset_measurement_in_offline_mode()

    def canoe_step_measurement_event_in_single_step(self) -> bool:
        """
        Steps the measurement event in single step mode.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self._source.step_measurement_event_in_single_step()

    def canoe_get_measurement_index(self) -> int:
        """
        Gets the measurement index.
        
        Returns:
            int: The measurement index.
        """
        return self._source.get_measurement_index()

    def canoe_set_measurement_index(self, index: int) -> bool:
        """
        Sets the measurement index.
        
        Args:
            index (int): The measurement index to set.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self._source.set_measurement_index(index)

    def canoe_send_diag_request(self, diag_ecu_qualifier_name: str, request: str, request_in_bytes=True, return_sender_name=False, response_in_bytearray=False, timeout: float=30, poll_s: float=0.01, **kwargs) -> Union[str, dict]:
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
        return self._source.send_diag_request(diag_ecu_qualifier_name, request, request_in_bytes, return_sender_name, response_in_bytearray, timeout, poll_s, **kwargs)

    def canoe_control_tester_present(self, diag_ecu_qualifier_name: str, value: bool) -> bool:
        """
        Controls the tester present signal.
        
        Args:
            diag_ecu_qualifier_name (str): The diagnostic ECU qualifier name.
            value (bool): The value to set for the tester present signal.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self._source.control_tester_present(diag_ecu_qualifier_name, value)

    def canoe_define_system_variable(self, sys_var_name: str, value: Union[int, float, str], read_only: bool=False) -> object:
        """
        Defines a system variable.
        
        Args:
            sys_var_name (str): The name of the system variable.
            value (Union[int, float, str]): The value of the system variable.
            read_only (bool): Whether the system variable is read-only.
        
        Returns:
            object: The created system variable object.
        """
        return self._source.define_system_variable(sys_var_name, value, read_only)

    def canoe_get_system_variable_value(self, sys_var_name: str, return_symbolic_name: bool=False, return_timestamp: bool=False, enable_events: bool=True) -> Union[int, float, str, None, tuple]:
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
        return self._source.get_system_variable_value(sys_var_name, return_symbolic_name, return_timestamp, enable_events)

    def canoe_get_all_namespace_names(self) -> list[str]:
        """Returns all namespace names from the current application."""
        return self._source.get_all_namespace_names()

    def canoe_get_all_variables_in_namespace(self, namespace_name: str) -> list[dict]:
        """Returns all variables in the specified namespace."""
        return self._source.get_all_variables_in_namespace(namespace_name)

    def canoe_set_system_variable_value(self, sys_var_name: str, value: Union[int, float, str]) -> bool:
        """
        Sets the value of a system variable.
        
        Args:
            sys_var_name (str): The name of the system variable.
            value (Union[int, float, str]): The value to set.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self._source.set_system_variable_value(sys_var_name, value)

    def canoe_set_system_variable_array_values(self, sys_var_name: str, value: tuple, index: int=0) -> bool:
        """
        Sets the values of a system variable array.
        
        Args:
            sys_var_name (str): The name of the system variable.
            value (tuple): The values to set.
            index (int): The index to set the values at.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self._source.set_system_variable_array_values(sys_var_name, value, index)

    def canoe_ui_activate_desktop(self, name: str) -> bool:
        """
        Activates a desktop by name.
        
        Args:
            name (str): The name of the desktop to activate.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self._source.ui_activate_desktop(name)

    def canoe_ui_open_baudrate_dialog(self) -> bool:
        """
        Opens the baudrate dialog.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self._source.ui_open_baudrate_dialog()

    def canoe_write_text_in_write_window(self, text: str) -> bool:
        """
        Writes text in the write window.
        
        Args:
            text (str): The text to write.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self._source.write_text_in_write_window(text)

    def canoe_read_text_from_write_window(self) -> Union[str, None]:
        """
        Reads text from the write window.
        
        Returns:
            Union[str, None]: The text from the write window or None if not found.
        """
        return self._source.read_text_from_write_window()

    def canoe_clear_write_window_content(self) -> bool:
        """
        Clears the content of the write window.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self._source.clear_write_window_content()

    def canoe_copy_write_window_content(self) -> bool:
        """
        Copies the content of the write window.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self._source.copy_write_window_content()

    def canoe_enable_write_window_output_file(self, output_file: str, tab_index=None) -> bool:
        """
        Enables the write window output file.
        
        Args:
            output_file (str): The output file path.
            tab_index (Optional[int]): The tab index to enable the output file for.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self._source.enable_write_window_output_file(output_file, tab_index)

    def canoe_disable_write_window_output_file(self, tab_index=None) -> bool:
        """
        Disables the write window output file.
        
        Args:
            tab_index (Optional[int]): The tab index to disable the output file for.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self._source.disable_write_window_output_file(tab_index)

    def canoe_get_canoe_version_info(self) -> dict[str, str | int]:
        """
        Gets the version information of the CANoe application.
        
        Returns:
            dict: The version information.
        """
        return self._source.get_canoe_version_info()

