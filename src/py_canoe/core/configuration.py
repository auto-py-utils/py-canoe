from typing import TYPE_CHECKING, Iterable, Sequence, Union

from py_canoe.core.child_elements.test_module import TestModule
if TYPE_CHECKING:
    from py_canoe.core.application import Application
    from py_canoe.core.child_elements.measurement_setup import Logging, ExporterSymbol, Message
    from py_canoe.core.child_elements.test_configurations import TestConfiguration
import os
import re
import time
from fnmatch import fnmatchcase
import win32com.client

from py_canoe.core.child_elements.c_libraries import CLibraries
from py_canoe.core.child_elements.communication_setup import CommunicationSetup
from py_canoe.core.child_elements.distributed_mode import DistributedMode
from py_canoe.core.child_elements.fdx_files import FDXFiles
from py_canoe.core.child_elements.general_setup import GeneralSetup
from py_canoe.core.child_elements.measurement_setup import MeasurementSetup
from py_canoe.core.child_elements.database_setup import Databases
from py_canoe.core.child_elements.replay_collection import ReplayCollection
from py_canoe.core.child_elements.simulation_setup import SimulationSetup
from py_canoe.core.child_elements.test_configurations import TestConfigurations
from py_canoe.core.child_elements.test_setup import TestSetup
from py_canoe.core.child_elements.test_tree_elements import TestTreeElements, TestTreeElementType
from py_canoe.core.child_elements.test_unit import TestUnit
from py_canoe.helpers.common import logger, wait


class ConfigurationEvents:
    def __init__(self):
        self.CONFIGURATION_CLOSED = False
        self.SYSTEM_VARIABLES_DEFINITION_CHANGED = False

    def OnClose(self):
        self.CONFIGURATION_CLOSED = True

    def OnSystemVariablesDefinitionChanged(self):
        self.SYSTEM_VARIABLES_DEFINITION_CHANGED = True


class Configuration:
    """
    The Configuration object represents the active configuration.
    """
    def __init__(self, app: 'Application'):
        self.app = app
        self.bus_types = self.app.bus_types
        self.com_object = win32com.client.Dispatch(self.app.com_object.Configuration)
        # self.configuration_events: ConfigurationEvents = win32com.client.WithEvents(self.com_object, ConfigurationEvents)
        self.configuration_test_configurations = lambda: self.test_configurations
        self.configuration_test_setup = lambda: self.test_setup
        self.__test_setup_environments = self.configuration_test_setup().test_environments.fetch_all_test_environments()
        self.__test_configurations = self.configuration_test_configurations().fetch_all_test_configurations()
        self.__test_modules = list()
        self.__test_units = list()

    def fetch_test_modules(self):
        for te_name, te_inst in self.__test_setup_environments.items():
            for tm_name, tm_inst in te_inst.get_all_test_modules().items():
                # A TestSetupItem object that either can be a TSTestModule object or a TestSetupFolder object.
                # TestSetupFolder有items，包含TestSetupItems
                self.__test_modules.append({'name': tm_name, 'object': tm_inst, 'environment': te_name})

    def fetch_test_units(self):
        for tc_name, tc_inst in self.__test_configurations.items():
            for tu_index in range(1, tc_inst.test_units.count + 1):
                tu_inst = tc_inst.test_units.item(tu_index)
                self.__test_units.append({'name': tu_inst.name, 'object': tu_inst, 'test_configuration': tc_name})
        return self.__test_units

    @property
    def c_libraries(self) -> 'CLibraries':
        return CLibraries(self.com_object.CLibraries)

    @property
    def comment(self) -> str:
        return self.com_object.Comment

    @property
    def communication_setup(self) -> 'CommunicationSetup':
        return CommunicationSetup(self.com_object.CommunicationSetup)

    @property
    def distributed_mode(self) -> 'DistributedMode':
        return DistributedMode(self.com_object.DistributedMode)

    @property
    def fdx_enabled(self) -> bool:
        return self.com_object.FDXEnabled

    @fdx_enabled.setter
    def fdx_enabled(self, enabled: bool):
        self.com_object.FDXEnabled = enabled

    @property
    def fdx_files(self) -> 'FDXFiles':
        return FDXFiles(self.com_object.FDXFiles)

    @property
    def full_name(self) -> str:
        return self.com_object.FullName

    @property
    def general_setup(self) -> 'GeneralSetup':
        return GeneralSetup(self.com_object.GeneralSetup)

    # GlobalTcpIpStackSetting

    @property
    def mode(self) -> int:
        return self.com_object.Mode

    @mode.setter
    def mode(self, type: int):
        self.com_object.Mode = type

    @property
    def modified(self) -> bool:
        return self.com_object.Modified

    @modified.setter
    def modified(self, modified: bool):
        self.com_object.Modified = modified

    @property
    def name(self) -> str:
        return self.com_object.Name

    # NETTargetFramework

    @property
    def offline_setup(self) -> 'MeasurementSetup':
        return MeasurementSetup(self.com_object.OfflineSetup)

    @property
    def online_setup(self) -> 'MeasurementSetup':
        return MeasurementSetup(self.com_object.OnlineSetup)

    @property
    def path(self) -> str:
        return self.com_object.Path

    @property
    def read_only(self) -> bool:
        return self.com_object.ReadOnly

    @property
    def saved(self) -> bool:
        return self.com_object.Saved

    # Sensor

    @property
    def simulation_setup(self) -> 'SimulationSetup':
        return SimulationSetup(self.com_object.SimulationSetup)

    # StandaloneMode

    # StartValueList

    # SymbolMappings

    @property
    def test_configurations(self) -> 'TestConfigurations':
        return TestConfigurations(self.com_object.TestConfigurations)

    @property
    def test_setup(self) -> 'TestSetup':
        return TestSetup(self.com_object.TestSetup)

    # UserFiles

    # VTSystem

    def compile_and_verify(self) -> None:
        self.com_object.CompileAndVerify()
        logger.info("CAPL compilation completed successfully.")

    def get_compilation_result(self) -> dict[str, object]:
        """Get CAPL compilation result with error details.

        Compiles all CAPL code in the current configuration and returns
        detailed result including success status and error information.

        Returns:
            dict: Dictionary with keys:
                - "success" (bool): True if compilation succeeded, False otherwise
                - "error" (str | None): Error message if compilation failed, None on success

        Example:
            >>> result = config.get_compilation_result()
            >>> if result["success"]:
            ...     print("Compilation OK")
            ... else:
            ...     print(f"Compilation failed: {result['error']}")
        """
        result = self._compile_and_verify_internal()
        if result["success"]:
            logger.info('CAPL compilation succeeded')
        else:
            logger.warning(f'CAPL compilation failed: {result["error"]}')
        return result

    def run_compilation(self) -> bool:
        """Run CAPL compilation and return success status.

        Compiles all CAPL code in the current configuration.
        Use get_compilation_result() if you need error details.

        Returns:
            bool: True if compilation succeeded, False otherwise

        Example:
            >>> if config.run_compilation():
            ...     print("Compilation OK")
        """
        result = self._compile_and_verify_internal()
        if result["success"]:
            logger.info('CAPL compilation passed')
        else:
            logger.warning(f'CAPL compilation failed: {result["error"]}')
        return result["success"]

    def _compile_and_verify_internal(self) -> dict[str, object]:
        try:
            self.com_object.CompileAndVerify()
            return {"success": True, "error": None}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def save(self, path: str = "", prompt_user: bool = False) -> bool:
        try:
            if self.saved:
                logger.warning("CANoe configuration is already saved.")
                return True
            if path == "":
                path = self.full_name
            self.com_object.Save(path, prompt_user)
            logger.info("CANoe configuration saved successfully.")
            return True
        except Exception as e:
            logger.error(f"Error saving CANoe configuration: {e}")
            return False

    def save_as(self, path: str, major: int, minor: int, prompt_user: bool = False, create_dir: bool = True) -> bool:
        try:
            if create_dir:
                dir_path = os.path.dirname(path)
                if dir_path:
                    os.makedirs(dir_path, exist_ok=True)
                    logger.info(f'Created directory {dir_path} for saving configuration')
            self.com_object.SaveAs(path, major, minor, prompt_user)
            logger.info(f"CANoe configuration saved as {path} successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving CANoe configuration as '{path}': {e}")
            return False

    def get_can_bus_statistics(self, channel: int) -> dict:
        try:
            can_stat_obj = self.online_setup.bus_statistics.BusStatistic(self.bus_types['CAN'], channel)
            keys = [
                'BusLoad', 'ChipState', 'Error', 'ErrorTotal', 'Extended', 'ExtendedTotal',
                'ExtendedRemote', 'ExtendedRemoteTotal', 'Overload', 'OverloadTotal', 'PeakLoad',
                'RxErrorCount', 'Standard', 'StandardTotal', 'StandardRemote', 'StandardRemoteTotal',
                'TxErrorCount'
            ]
            can_bus_stat_info = {key.lower(): getattr(can_stat_obj, key) for key in keys}
            logger.info(f'CAN bus channel ({channel}) statistics:')
            for key, value in can_bus_stat_info.items():
                logger.info(f"    {key}: {value}")
            return can_bus_stat_info
        except Exception as e:
            logger.error(f"Error retrieving CAN bus statistics for channel {channel}: {e}")
            return {}

    def add_offline_source_log_file(self, absolute_log_file_path: str) -> bool:
        try:
            if not os.path.isfile(absolute_log_file_path):
                logger.error(f"Error: Offline source log file '{absolute_log_file_path}' does not exist.")
                return False
            offline_sources_obj = self.com_object.OfflineSetup.Source.Sources
            offline_sources_files = [offline_sources_obj.Item(i) for i in range(1, offline_sources_obj.Count + 1)]
            file_already_added = any([file == absolute_log_file_path for file in offline_sources_files])
            if file_already_added:
                logger.warning(f"Offline source log file '{absolute_log_file_path}' is already added.")
            else:
                offline_sources_obj.Add(absolute_log_file_path)
                logger.info(f'File "{absolute_log_file_path}" added as offline source')
            return True
        except Exception as e:
            logger.error(f"Error adding offline source log file '{absolute_log_file_path}': {e}")
            return False

    def set_replay_block_file(self, block_name: str, recording_file_path: str) -> bool:
        try:
            replay_collection_obj = ReplayCollection(self.com_object.SimulationSetup.ReplayCollection)
            replay_blocks_obj_dict = dict()
            for i in range(1, replay_collection_obj.count + 1):
                replay_block_obj = replay_collection_obj.item(i)
                replay_blocks_obj_dict[replay_block_obj.name] = replay_block_obj
            if block_name in replay_blocks_obj_dict:
                replay_blocks_obj_dict[block_name].path = recording_file_path
                logger.info(f"Replay block path for '{block_name}' set to '{recording_file_path}'")
                return True
            else:
                logger.warning(f"Replay block '{block_name}' not found")
                return False
        except Exception as e:
            logger.error(f"Error setting replay block file for '{block_name}': {e}")
            return False

    def control_replay_block(self, block_name: str, start_stop: bool) -> bool:
        try:
            replay_collection_obj = ReplayCollection(self.com_object.SimulationSetup.ReplayCollection)
            replay_blocks_obj_dict = dict()
            for i in range(1, replay_collection_obj.count + 1):
                replay_block_obj = replay_collection_obj.item(i)
                replay_blocks_obj_dict[replay_block_obj.name] = replay_block_obj
            if block_name in replay_blocks_obj_dict:
                if start_stop:
                    replay_blocks_obj_dict[block_name].start()
                    logger.info(f"Replay block '{block_name}' started")
                else:
                    replay_blocks_obj_dict[block_name].stop()
                    logger.info(f"Replay block '{block_name}' stopped")
                return True
            else:
                logger.warning(f"Replay block '{block_name}' not found")
                return False
        except Exception as e:
            logger.error(f"Error controlling replay block '{block_name}': {e}")
            return False

    def enable_disable_replay_block(self, block_name: str, enable_disable: bool) -> bool:
        try:
            replay_collection_obj = ReplayCollection(self.com_object.SimulationSetup.ReplayCollection)
            replay_blocks_obj_dict = dict()
            for i in range(1, replay_collection_obj.count + 1):
                replay_block_obj = replay_collection_obj.item(i)
                replay_blocks_obj_dict[replay_block_obj.name] = replay_block_obj
            if block_name in replay_blocks_obj_dict:
                replay_blocks_obj_dict[block_name].enabled = enable_disable
                logger.info(f"Replay block '{block_name}' {'enabled' if enable_disable else 'disabled'}")
                return True
            else:
                logger.warning(f"Replay block '{block_name}' not found")
                return False
        except Exception as e:
            logger.error(f"Error enabling/disabling replay block '{block_name}': {e}")
            return False

    def get_test_configurations(self) -> dict[str, 'TestConfiguration']:
        try:
            return self.__test_configurations
        except Exception as e:
            logger.error(f'failed to get test configurations. {e}')
            return {}

    def get_test_configurations_cases_result(self, test_conf_name: str) -> dict:

        if not test_conf_name: 
            logger.warning("test_conf_name parameter is required.")
            return {}
        
        verdict = {
            0: "NotAvailable",
            1: "Passed",
            2: "Failed",
            3: "None",
            4: "Inconclusive",
            5: "ErrorInTestSystem"
        }
        
        test_cases = {}
        for t_conf_name in self.__test_configurations.keys():
            if t_conf_name != test_conf_name: continue
            test_units_obj: dict[str, TestUnit] = self.__test_configurations[t_conf_name].test_units.fetch_all_test_units()
            report_path = self.__test_configurations[t_conf_name].report.full_path
            for tn_name in test_units_obj.keys():
                test_elements: TestTreeElements = test_units_obj[tn_name].elements
                test_elements.get_test_tree_element_cases(test_cases)
        
        return {
            name: {
                "enabled": value["tte_obj"].enabled,
                "verdict": value["tte_obj"].verdict,
                "verdict_name": verdict.get(value["tte_obj"].verdict, "Unknown"),
                "report_path": report_path
            }
            for name, value in test_cases.items()
        }
    


    def get_top_test_configurations_elements(self) -> dict:
        return self.test_configurations.get_top_test_configurations_elements()
    
    def get_all_test_configurations_cases(self) -> dict:
        return self.test_configurations.get_all_test_configurations_cases()

    def enable_test_configurations_cases(self, tc_obj,
                                         enable_patterns: Sequence[str] = (), 
                                         disable_patterns: Sequence[str] = (), 
                                         match_by: str = "name") -> None:
        if match_by not in ("name","group", "fixture"):
            logger.warning(f'Invalid match_by="{match_by}", falling back to "name".')
            match_by = "name"

        if isinstance(enable_patterns, str):
            enable_patterns = [enable_patterns]
        if isinstance(disable_patterns, str):
            disable_patterns = [disable_patterns]

        if not enable_patterns and not disable_patterns:
            return

        all_test_all_elements = self.get_top_test_configurations_elements()
        all_test_cases = self.get_all_test_configurations_cases()

        if not (all_test_cases or all_test_all_elements):
            logger.warning(f'No test cases found in test module ({tc_obj}).')
            return

        if match_by in ("group", "fixture"):
            match_flag =False
            for all_ttes in all_test_all_elements.values():
                for name, tts_obj in all_ttes.items():
                    if tts_obj.type in (TestTreeElementType.TEST_GROUP, TestTreeElementType. TEST_FIXTURE):
                        for pattern in enable_patterns:
                            if self._match_test_case_name(name, pattern):
                                match_flag = True
                                tts_obj.enabled = True
            if not match_flag:
                logger.warning(f'Test configurations "{tc_obj}" has no test case titles available;'
                                f'title patterns will not match anything, skipping selection.'
                )
                return

        for tc_name, tc in all_test_cases.items():
            should_enable = False
            should_disable = False

            for pattern in disable_patterns:
                if self._match_test_case_name(tc_name, pattern):
                    should_disable = True
                    break

            if not should_disable:
                for pattern in enable_patterns:
                    if self._match_test_case_name(tc_name, pattern):
                        should_enable = True
                        break

            if should_disable:
                if tc['tte_obj'].enabled:
                    tc['tte_obj'].enabled = False
                    logger.info(f'Test case "{tc_name}" disabled by pattern match.')
            elif should_enable:
                if not tc['tte_obj'].enabled:
                    tc['tte_obj'].enabled = True
                    logger.info(f'Test case "{tc_name}" enabled by pattern match.')



    def execute_all_test_configurations(self, enable_test_case: Sequence[str] = (), 
                                        disable_test_case: Sequence[str] = (),
                                        match_by: str = "name",
                                        wait_for_completion: bool = True) -> bool:
        try:
            for tc_name, tc_inst in self.__test_configurations.items():
                self.enable_test_configurations_cases(self.__test_configurations[tc_name],
                                                      enable_test_case,
                                                      disable_test_case,
                                                      match_by)
                tc_inst.start()
                if wait_for_completion:
                    while tc_inst.running:
                        wait(1)
                    logger.info(f'completed executing test configuration ({tc_name}) with verdict {tc_inst.test_configuration_events.VERDICT.name}')
            return True
        except Exception as e:
            logger.error(f'failed to execute test configuration. {e}')
            return False

    def stop_all_test_configurations(self,) -> bool:
        try:
            for _, tc_inst in self.__test_configurations.items():
                if tc_inst.running:
                    tc_inst.stop()
            return True
        except Exception as e:
            logger.error(f'failed to stop test configuration. {e}')
            return False

    def execute_test_configuration(self, tc_name: str, enable_test_case: Sequence[str] = (),
                                   disable_test_case: Sequence[str] = (),
                                   match_by: str = "name",
                                   wait_for_completion: bool = True) -> bool:
        try:
            if tc_name in self.__test_configurations.keys():
                self.enable_test_configurations_cases(self.__test_configurations[tc_name],
                                                      enable_test_case,
                                                      disable_test_case,
                                                      match_by)
                
                tc_inst = self.__test_configurations[tc_name]
                tc_inst.start()
                if wait_for_completion:
                    while tc_inst.running:
                        wait(1)
                    logger.info(f'completed executing test configuration ({tc_name}) with verdict {tc_inst.test_configuration_events.VERDICT.name}')
                return True
            else:
                logger.warning(f'test configuration "{tc_name}" not found in configuration')
                return False
        except Exception as e:
            logger.error(f'failed to execute test configuration. {e}')
            return False

    def stop_test_configuration(self, tc_name: str) -> bool:
        try:
            if tc_name in self.__test_configurations.keys():
                tc_inst = self.__test_configurations[tc_name]
                if tc_inst.running:
                    tc_inst.stop()
                else:
                    logger.warning(f'test configuration "{tc_name}" is not running')
                return True
            else:
                logger.warning(f'test configuration "{tc_name}" not found in configuration')
                return False
        except Exception as e:
            logger.error(f'failed to stop test configuration. {e}')
            return False

    def get_test_environments(self) -> dict:
        try:
            return self.__test_setup_environments
        except Exception as e:
            logger.error(f'failed to get test environments. {e}')
            return {}

    def get_test_modules(self, env_name: str) -> dict:
        try:
            test_environments = self.get_test_environments()
            if len(test_environments) > 0:
                if env_name in test_environments.keys():
                    return test_environments[env_name].get_all_test_modules()
                else:
                    logger.warning(f'"{env_name}" not found in configuration')
                    return {}
            else:
                logger.warning('Zero test environments found in configuration. Not possible to fetch test modules')
                return {}
        except Exception as e:
            logger.error(f'failed to get test modules. {e}')
            return {}

    @staticmethod
    def _match_test_case_name(name: str, pattern: str) -> bool:
        """Check if a test case name matches a pattern.

        Supports two matching modes:
        - Regex: patterns starting with '(?i)' or '(?' are treated as regex.
                 Also treats as regex if the pattern contains regex metacharacters
                 like '^', '$', '[', ']', '+', '{', '}' (but not '*' or '?'
                 alone, as those are valid glob chars).
        - Wildcard (default): uses fnmatch-style patterns where:
                * matches everything
                ? matches any single character
                [seq] matches any character in seq
                [!seq] matches any character not in seq

        Args:
            name: The test case name to check.
            pattern: The pattern to match against.

        Returns:
            bool: True if the name matches the pattern.
        """
        # Treat as regex if it starts with '(?' or contains regex-specific syntax.
        # Distinguish from fnmatch glob by inspecting bracket/brace contents:
        #   - [...\d...] or [[:alpha:]] → regex (fnmatch doesn't support \d, POSIX classes)
        #   - {3} or {1,3}             → regex quantifier (digits inside braces)
        #   - {foo,bar}                → fnmatch alternation (commas inside braces)
        #
        # Why not just try re.search() first and fall back to fnmatch on
        # re.error? Because an *invalid* regex raises re.error and would fall
        # back correctly, BUT a *valid* regex that the user actually meant as a
        # glob (e.g. "TC_[0-9]") would be silently interpreted as regex
        # and match differently. The heuristic below keeps glob the default
        # and only escalates to regex when we see unambiguous regex markers.
        is_regex = pattern.startswith('(?')
        if not is_regex:
            # Check for unambiguous regex markers outside bracket context
            # (strip [...] and {...} first to avoid false positives from glob syntax)
            stripped = re.sub(r'\[.*?\]', '', pattern)
            stripped = re.sub(r'\{.*?\}', '', stripped)
            if re.search(r'[+^$]|\\[dDwWsSbB]|\\\(|\\\{|\\\[' , stripped):
                is_regex = True
            # Check bracket contents for regex-specific escapes
            # Use greedy match to handle nested brackets like [[:alpha:]]
            for m in re.finditer(r'\[(.+)\]', pattern):
                if re.search(r'\\[dDwWsSbB]|\[:\w+:\]', m.group(1)):
                    is_regex = True
                    break
            # Check brace contents:
            #   {3} or {1,3} → regex quantifier (digits, optionally with comma)
            #   {foo,bar}    → fnmatch alternation (text with comma, Python fnmatch
            #                  doesn't expand braces so it matches literally)
            for m in re.finditer(r'\{([^}]+)\}', pattern):
                content = m.group(1)
                if re.match(r'^\d+$', content) or re.match(r'^\d+,\d*$', content):
                    is_regex = True
                    break
        if is_regex:
            try:
                return bool(re.search(pattern, name))
            except re.error:
                # Fall back to literal match if regex is invalid
                return name == pattern
        # Otherwise use fnmatch wildcard matching
        return fnmatchcase(name, pattern)

    def _apply_test_case_selection(self, tm_obj:TestModule, enable_patterns: Sequence[str], disable_patterns: Sequence[str], match_by: str = "name") -> None:
        """Apply test case enable/disable selections based on patterns.

        Iterates all test cases in the test module and matches each name (or
        title, see ``match_by``) against the given patterns.
        disable_patterns takes precedence over enable_patterns.

        Args:
            tm_obj: The TestModule COM object.
            enable_patterns: Patterns for test cases to enable.
            disable_patterns: Patterns for test cases to disable.
            match_by: Which test case attribute to match the patterns against.
                Either "name" (default) or "title".
        """
        if match_by not in ("name", "title"):
            logger.warning(f'Invalid match_by="{match_by}", falling back to "name".')
            match_by = "name"

        # Coerce a bare string into a single-element sequence. Passing a string
        # (e.g. "XM_CSflash_FUNC_00*") would otherwise be iterated character by
        # character, and the '*' character alone would match every test case.
        if isinstance(enable_patterns, str):
            enable_patterns = [enable_patterns]
        if isinstance(disable_patterns, str):
            disable_patterns = [disable_patterns]

        if not enable_patterns and not disable_patterns:
            return

        all_test_cases = tm_obj.get_all_test_cases()

        if not all_test_cases:
            logger.warning(f'No test cases found in test module ({tm_obj.name}).')
            return

        # When matching by title, check up front whether any title is available.
        # Many module types (e.g. CAPL test modules) do not expose a Title at
        # all. If no title exists at all, there is nothing to match against,
        # so warn once and skip the whole matching loop (matching empty
        # titles would never hit and just wastes a full iteration).
        if match_by == "title" and not any(tc.title for tc in all_test_cases.values()):
            logger.warning(
                f'Test module "{tm_obj.name}" has no test case titles available; '
                f'title patterns will not match anything, skipping selection.'
            )
            return

        for tc_name, tc in all_test_cases.items():
            # Match against the requested attribute (name or title).
            # print(f"Checking test case: {tc_name}, title: {tc.title}, ident: {tc.ident}, enabled: {tc.enabled}, verdict: {tc.verdict_name}")
            match_value = tc.title if match_by == "title" else tc.name
            should_enable = False
            should_disable = False

            # Check disable patterns first (higher priority)
            for pattern in disable_patterns:
                if self._match_test_case_name(match_value, pattern):
                    should_disable = True
                    break

            # Check enable patterns only if not already matched by disable
            if not should_disable:
                for pattern in enable_patterns:
                    if self._match_test_case_name(match_value, pattern):
                        should_enable = True
                        break

            if should_disable:
                if tc.enabled:
                    tc.enabled = False
                    logger.info(f'Test case "{tc_name}" disabled by pattern match.')
            elif should_enable:
                if not tc.enabled:
                    tc.enabled = True
                    logger.info(f'Test case "{tc_name}" enabled by pattern match.')

    def execute_test_module(self, test_module_name: str, enable_test_cases: Sequence[str] = (), disable_test_cases: Sequence[str] = (), match_by: str = "name") -> int:
        try:
            test_verdict = {0: 'NotAvailable',
                            1: 'Passed',
                            2: 'Failed',
                            3: 'None (not available for test modules)',
                            4: 'Inconclusive (not available for test modules)',
                            5: 'ErrorInTestSystem (not available for test modules)', }
            execution_result = 0
            tm_obj = self._find_test_module(test_module_name)
            if tm_obj is not None:
                self._apply_test_case_selection(tm_obj, enable_test_cases, disable_test_cases, match_by=match_by)
                tm_obj.start()
                tm_obj.wait_for_completion()
                execution_result = tm_obj.verdict
                logger.info(f'test module "{test_module_name}", verdict = {test_verdict[execution_result]}')
            return execution_result
        except Exception as e:
            logger.error(f'failed to execute test module. {e}')
            return 0

    def _find_test_module(self, test_module_name: str) -> TestModule:
        """Find a test module by name from the cached test modules list.

        Returns:
            TestModule wrapper object if found, None otherwise.
        """
        for tm in self.__test_modules:
            if tm['name'] == test_module_name:
                return tm['object']
        logger.warning(f'test module "{test_module_name}" not found.')
        return None

    def get_test_module_result(self, test_module_name: str, report_timeout: float = 30.0) -> dict:
        """Get test module execution result including report path and test case verdicts.

        Should be called after execute_test_module() to retrieve the results.

        Note: This method does NOT depend on the module's started state. It reads
        the verdict and report information directly from the test module object,
        and waits (up to ``report_timeout`` seconds) for the report-generated
        event if it has not fired yet. The returned ``test_cases`` are live
        ``TestCase`` objects, so accessing their attributes (e.g. ``verdict``,
        ``enabled``) reads the latest values from CANoe.

        Args:
            test_module_name (str): name of the test module.
            report_timeout (float): maximum time in seconds to wait for the
                report-generated event before giving up. Defaults to 30.0.

        Returns:
            dict: A dictionary with keys:
                - "verdict" (int): overall test module verdict (0-5)
                - "verdict_name" (str): human-readable verdict name
                - "report" (dict): report information with keys:
                    - "success" (bool): whether report generation succeeded
                    - "source_full_name" (str): XML report path
                    - "generated_full_name" (str): HTML report path
                - "test_cases" (dict[str, TestCase]): mapping of test case names
                  to live TestCase objects (use .name/.enabled/.verdict/.title)
        """
        try:
            tm_obj = self._find_test_module(test_module_name)
            if tm_obj is None:
                return {}

            # Wait for the report-generated event (bounded by report_timeout) so
            # the report paths are populated. If it already fired, this returns
            # immediately. We do NOT gate on TM_STARTED, because the module may
            # have been stopped (which resets TM_STARTED) by the time results
            # are requested. Use a monotonic clock so the wait is not
            # skewed by GIL/thread scheduling.
            deadline = time.monotonic() + report_timeout
            while not tm_obj.test_module_events.TM_REPORT_GENERATED and time.monotonic() < deadline:
                wait(0.01)
            if not tm_obj.test_module_events.TM_REPORT_GENERATED:
                logger.warning(
                    f'Test module "{test_module_name}" report was not generated '
                    f'within {report_timeout}s; report paths may be empty.'
                )

            # overall verdict
            verdict = tm_obj.verdict
            verdict_name = tm_obj.VALUE_TABLE_VERDICT.get(verdict, "Unknown")

            # report information from event sink
            report_info = tm_obj.test_module_events.TEST_REPORT_INFORMATION
            report = {
                "success": report_info.get("success", False),
                "source_full_name": report_info.get("source_full_name", ""),
                "generated_full_name": report_info.get("generated_full_name", ""),
            }

            test_cases = tm_obj.get_all_test_cases()

            return {
                "verdict": verdict,
                "verdict_name": verdict_name,
                "report": report,
                "test_cases": test_cases
            }

        except Exception as e:
            logger.error(f'failed to get test module result for "{test_module_name}": {e}')
            return {}

    def stop_test_module(self, test_module_name: str):
        try:
            tm_obj = self._find_test_module(test_module_name)
            if tm_obj is not None:
                tm_obj.stop()
                logger.info(f'test module "{test_module_name}" stopped.')
        except Exception as e:
            logger.error(f'failed to stop test module. {e}')

    def execute_all_test_modules_in_test_env(self, env_name: str, enable_test_cases: Sequence[str] = (), disable_test_cases: Sequence[str] = (), match_by: str = "name"):
        try:
            test_modules = self.get_test_modules(env_name=env_name)
            if test_modules:
                for tm_name in test_modules.keys():
                    self.execute_test_module(
                        tm_name,
                        enable_test_cases=enable_test_cases,
                        disable_test_cases=disable_test_cases,
                        match_by=match_by,
                    )
            else:
                logger.warning(f'test modules not available in "{env_name}" test environment')
        except Exception as e:
            logger.error(f'failed to execute all test modules in "{env_name}" test environment. {e}')

    def stop_all_test_modules_in_test_env(self, env_name: str):
        try:
            test_modules = self.get_test_modules(env_name=env_name)
            if test_modules:
                for tm_name in test_modules.keys():
                    self.stop_test_module(tm_name)
            else:
                logger.warning(f'test modules not available in "{env_name}" test environment')
        except Exception as e:
            logger.error(f'failed to stop all test modules in "{env_name}" test environment. {e}')

    def execute_all_test_environments(self):
        try:
            test_environments = self.get_test_environments()
            if len(test_environments) > 0:
                for test_env_name in test_environments.keys():
                    logger.info(f'executing test environment "{test_env_name}". please wait...')
                    self.execute_all_test_modules_in_test_env(test_env_name)
                    logger.info(f'completed executing test environment "{test_env_name}"')
            else:
                logger.warning('Zero test environments found in configuration')
        except Exception as e:
            logger.error(f'failed to execute all test environments. {e}')

    def stop_all_test_environments(self):
        try:
            test_environments = self.get_test_environments()
            if len(test_environments) > 0:
                for test_env_name in test_environments.keys():
                    logger.info(f'stopping test environment "{test_env_name}" execution. please wait...')
                    self.stop_all_test_modules_in_test_env(test_env_name)
                    logger.info(f'completed stopping test environment "{test_env_name}"')
            else:
                logger.warning('Zero test environments found in configuration')
        except Exception as e:
            logger.error(f'failed to stop all test environments. {e}')

    def add_database(self, database_file: str, database_channel: int, database_network: Union[str, None]=None) -> bool:
        try:
            if self.app.measurement.running:
                logger.warning("Cannot add database while measurement is running. Please stop the measurement first.")
                return False
            else:
                databases = Databases(self.com_object.GeneralSetup.DatabaseSetup.Databases)
                databases_info = {databases.item(index).full_name: databases.item(index) for index in range(1, databases.count + 1)}
                if database_file in databases_info.keys():
                    logger.warning(f'database "{database_file}" already added')
                    return False
                else:
                    if database_network:
                        database = databases.add_network(database_file, database_network)
                    else:
                        database = databases.add(database_file)
                    wait(0.5)
                    database.channel = database_channel
                    wait(0.5)
                    logger.info(f'database "{database_file}" added successfully to channel {database_channel}')
                    return True
        except Exception as e:
            logger.error(f"Error adding database '{database_file}': {e}")
            return False

    def remove_database(self, database_file: str, database_channel: int) -> bool:
        try:
            if self.app.measurement.running:
                logger.warning("Cannot remove database while measurement is running. Please stop the measurement first.")
                return False
            else:
                databases = Databases(self.com_object.GeneralSetup.DatabaseSetup.Databases)
                databases_info = {databases.item(index).full_name: databases.item(index) for index in range(1, databases.count + 1)}
                if database_file not in databases_info.keys():
                    logger.warning(f'database "{database_file}" not available to remove')
                    return False
                else:
                    for index in range(1, databases.count + 1):
                        database = databases.item(index)
                        if (database.full_name == database_file) and (database.channel == database_channel):
                            databases.remove(index)
                            wait(1)
                            logger.info(f'database "{database_file}" removed from channel "{database_channel}"')
                            return True
                    logger.warning(f'unable to remove database "{database_file}" from channel "{database_channel}"')
                    return False
        except Exception as e:
            logger.error(f"Error removing database '{database_file}': {e}")
            return False

    def get_mode(self) -> int:
        logger.info(f"CANoe Configuration mode = ({self.mode} - {'Offline mode' if self.mode == 1 else 'Online mode'})")
        return self.mode

    def set_mode(self, type: int) -> bool:
        try:
            if type in [0, 1]:
                self.mode = type
                logger.info(f"CANoe Configuration mode set to ({type} - {'Offline mode' if type == 1 else 'Online mode'})")
                return True
            else:
                logger.warning("Invalid mode type. Use 0 for Offline mode and 1 for Online mode.")
                return False
        except Exception as e:
            logger.error(f"Error setting CANoe Configuration mode: {e}")
            return False

    def get_logging_blocks(self) -> list['Logging']:
        blocks = []
        for i in range(1, self.online_setup.logging_collection.count + 1):
            logging_block = self.online_setup.logging_collection.item(i)
            blocks.append(logging_block)
        return blocks

    def add_logging_block(self, full_name: str) -> 'Logging':
        return self.online_setup.logging_collection.add(full_name)

    def remove_logging_block(self, index: int) -> None:
        if index == 0:
            raise ValueError("Logging blocks indexing starts from 1 and not 0.")
        self.online_setup.logging_collection.remove(index)

    def load_logs_for_exporter(self, logger_index: int) -> None:
        self.online_setup.logging_collection.item(logger_index).exporter.load()

    def get_symbols(self, logger_index: int) -> list['ExporterSymbol']:
        return self.online_setup.logging_collection.item(logger_index).exporter.symbols

    def get_messages(self, logger_index: int) -> list['Message']:
        return self.online_setup.logging_collection.item(logger_index).exporter.messages

    def add_filters_to_exporter(self, logger_index: int, full_names: 'Iterable'):
        expo_filter = self.online_setup.logging_collection.item(logger_index).exporter.filter
        for name in full_names:
            expo_filter.add(name)

    def start_export(self, logger_index: int):
        self.online_setup.logging_collection.item(logger_index).exporter.save()

    def start_stop_online_logging_block(self, full_name: str, start_stop: bool) -> bool:
        try:
            logging_blocks = self.get_logging_blocks()
            for logging_block in logging_blocks:
                if logging_block.full_name.lower() == full_name.lower():
                    if start_stop:
                        logging_block.trigger.start()
                        logger.info(f'logging block {full_name} started')
                    else:
                        logging_block.trigger.stop()
                        logger.info(f'logging block {full_name} stopped')
                    return True
            logger.warning(f'logging block {full_name} not found.')
            return False
        except Exception as e:
            logger.error(f"Error starting/stopping logging block {full_name}. {e}")

    def set_configuration_modified(self, modified: bool) -> None:
        self.modified = modified
