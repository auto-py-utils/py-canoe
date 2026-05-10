from typing import TYPE_CHECKING, Iterable, Union
if TYPE_CHECKING:
    from py_canoe.core.application import Application
    from py_canoe.core.child_elements.measurement_setup import Logging, ExporterSymbol, Message
    from py_canoe.core.child_elements.test_configurations import TestConfiguration
import os
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

    def save(self) -> bool:
        try:
            if self.saved:
                logger.warning("⚠️ CANoe configuration is already saved.")
                return True
            self.com_object.Save()
            logger.info("📢 CANoe configuration saved 💾 successfully 🎉")
            return True
        except Exception as e:
            logger.error(f"❌ Error saving CANoe configuration: {e}")
            return False

    def save_as(self, path: str, major: int, minor: int, prompt_user: bool = False, create_dir: bool = True) -> bool:
        try:
            if create_dir:
                dir_path = os.path.dirname(path)
                if dir_path:
                    os.makedirs(dir_path, exist_ok=True)
                    logger.info(f'📂 Created directory {dir_path} for saving configuration')
            self.com_object.SaveAs(path, major, minor, prompt_user)
            logger.info(f"📢 CANoe configuration saved 💾 as {path} successfully 🎉")
            return True
        except Exception as e:
            logger.error(f"❌ Error saving CANoe configuration as '{path}': {e}")
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
            logger.info(f'📜 CAN bus channel ({channel}) statistics:')
            for key, value in can_bus_stat_info.items():
                logger.info(f"    {key}: {value}")
            return can_bus_stat_info
        except Exception as e:
            logger.error(f"❌ Error retrieving CAN bus statistics for channel {channel}: {e}")
            return {}

    def add_offline_source_log_file(self, absolute_log_file_path: str) -> bool:
        try:
            if not os.path.isfile(absolute_log_file_path):
                logger.error(f"❌ Error: Offline source log file '{absolute_log_file_path}' does not exist.")
                return False
            offline_sources_obj = self.com_object.OfflineSetup.Source.Sources
            offline_sources_files = [offline_sources_obj.Item(i) for i in range(1, offline_sources_obj.Count + 1)]
            file_already_added = any([file == absolute_log_file_path for file in offline_sources_files])
            if file_already_added:
                logger.warning(f"⚠️ Offline source log file '{absolute_log_file_path}' is already added.")
            else:
                offline_sources_obj.Add(absolute_log_file_path)
                logger.info(f'📢 File "{absolute_log_file_path}" added as offline source')
            return True
        except Exception as e:
            logger.error(f"❌ Error adding offline source log file '{absolute_log_file_path}': {e}")
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
                logger.info(f"📢 Replay block path for '{block_name}' set to '{recording_file_path}'")
                return True
            else:
                logger.warning(f"⚠️ Replay block '{block_name}' not found")
                return False
        except Exception as e:
            logger.error(f"❌ Error setting replay block file for '{block_name}': {e}")
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
                    logger.info(f"📢 Replay block '{block_name}' started")
                else:
                    replay_blocks_obj_dict[block_name].stop()
                    logger.info(f"📢 Replay block '{block_name}' stopped")
                return True
            else:
                logger.warning(f"⚠️ Replay block '{block_name}' not found")
                return False
        except Exception as e:
            logger.error(f"❌ Error controlling replay block '{block_name}': {e}")
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
                logger.info(f"📢 Replay block '{block_name}' {'enabled' if enable_disable else 'disabled'}")
                return True
            else:
                logger.warning(f"⚠️ Replay block '{block_name}' not found")
                return False
        except Exception as e:
            logger.error(f"❌ Error enabling/disabling replay block '{block_name}': {e}")
            return False

    def get_test_configurations(self) -> dict[str, 'TestConfiguration']:
        try:
            return self.__test_configurations
        except Exception as e:
            logger.error(f'❌ failed to get test configurations. {e}')
            return {}

    def execute_all_test_configurations(self, wait_for_completion: bool = True) -> bool:
        try:
            for tc_name, tc_inst in self.__test_configurations.items():
                tc_inst.start()
                if wait_for_completion:
                    while tc_inst.running:
                        wait(1)
                    logger.info(f'🧪🧍 completed executing test configuration ({tc_name}) with verdict 👉 {tc_inst.test_configuration_events.VERDICT.name}')
                return True
        except Exception as e:
            logger.error(f'❌ failed to execute test configuration. {e}')
            return False

    def stop_all_test_configurations(self,) -> bool:
        try:
            for _, tc_inst in self.__test_configurations.items():
                if tc_inst.running:
                    tc_inst.stop()
            return True
        except Exception as e:
            logger.error(f'❌ failed to stop test configuration. {e}')
            return False

    def execute_test_configuration(self, tc_name: str, wait_for_completion: bool = True) -> bool:
        try:
            if tc_name in self.__test_configurations.keys():
                tc_inst = self.__test_configurations[tc_name]
                tc_inst.start()
                if wait_for_completion:
                    while tc_inst.running:
                        wait(1)
                    logger.info(f'🧪🧍 completed executing test configuration ({tc_name}) with verdict 👉 {tc_inst.test_configuration_events.VERDICT.name}')
                return True
            else:
                logger.warning(f'⚠️ test configuration "{tc_name}" not found in configuration')
                return False
        except Exception as e:
            logger.error(f'❌ failed to execute test configuration. {e}')
            return False

    def stop_test_configuration(self, tc_name: str) -> bool:
        try:
            if tc_name in self.__test_configurations.keys():
                tc_inst = self.__test_configurations[tc_name]
                if tc_inst.running:
                    tc_inst.stop()
                else:
                    logger.warning(f'⚠️ test configuration "{tc_name}" is not running')
                return True
            else:
                logger.warning(f'⚠️ test configuration "{tc_name}" not found in configuration')
                return False
        except Exception as e:
            logger.error(f'❌ failed to stop test configuration. {e}')
            return False

    def get_test_environments(self) -> dict:
        try:
            return self.__test_setup_environments
        except Exception as e:
            logger.error(f'❌ failed to get test environments. {e}')
            return {}

    def get_test_modules(self, env_name: str) -> dict:
        try:
            test_environments = self.get_test_environments()
            if len(test_environments) > 0:
                if env_name in test_environments.keys():
                    return test_environments[env_name].get_all_test_modules()
                else:
                    logger.warning(f'⚠️ "{env_name}" not found in configuration')
                    return {}
            else:
                logger.warning('⚠️ Zero test environments found in configuration. Not possible to fetch test modules')
                return {}
        except Exception as e:
            logger.error(f'❌ failed to get test modules. {e}')
            return {}

    def execute_test_module(self, test_module_name: str) -> int:
        try:
            test_verdict = {0: 'NotAvailable',
                            1: 'Passed',
                            2: 'Failed',
                            3: 'None (not available for test modules)',
                            4: 'Inconclusive (not available for test modules)',
                            5: 'ErrorInTestSystem (not available for test modules)', }
            execution_result = 0
            test_module_found = False
            test_env_name = ''
            for tm in self.__test_modules:
                if tm['name'] == test_module_name:
                    test_module_found = True
                    tm_obj = tm['object']
                    test_env_name = tm['environment']
                    logger.info(f'🔎 test module "{test_module_name}" found in "{test_env_name}"')
                    tm_obj.start()
                    tm_obj.wait_for_completion()
                    execution_result = tm_obj.verdict
                    break
                else:
                    continue
            if test_module_found and (execution_result == 1):
                logger.info(f'🧪🟢 test module "{test_env_name}.{test_module_name}" verdict = {test_verdict[execution_result]}')
            elif test_module_found and (execution_result != 1):
                logger.info(f'🧪🔴 test module "{test_env_name}.{test_module_name}" verdict = {test_verdict[execution_result]}')
            else:
                logger.warning(f'🧪⚠️ test module "{test_module_name}" not found. not possible to execute')
            return execution_result
        except Exception as e:
            logger.error(f'❌ failed to execute test module. {e}')
            return 0

    def stop_test_module(self, test_module_name: str):
        try:
            for tm in self.__test_modules:
                if tm['name'] == test_module_name:
                    tm['object'].stop()
                    test_env_name = tm['environment']
                    logger.info(f'🧪⏹️ test module "{test_module_name}" in test environment "{test_env_name}" stopped 🧍‍♂️')
            else:
                logger.warning(f'🧪⚠️ test module "{test_module_name}" not found. not possible to execute')
        except Exception as e:
            logger.error(f'❌ failed to stop test module. {e}')

    def execute_all_test_modules_in_test_env(self, env_name: str):
        try:
            test_modules = self.get_test_modules(env_name=env_name)
            if test_modules:
                for tm_name in test_modules.keys():
                    self.execute_test_module(tm_name)
            else:
                logger.warning(f'🧪⚠️ test modules not available in "{env_name}" test environment')
        except Exception as e:
            logger.error(f'🧪❌ failed to execute all test modules in "{env_name}" test environment. {e}')

    def stop_all_test_modules_in_test_env(self, env_name: str):
        try:
            test_modules = self.get_test_modules(env_name=env_name)
            if test_modules:
                for tm_name in test_modules.keys():
                    self.stop_test_module(tm_name)
            else:
                logger.warning(f'🧪⚠️ test modules not available in "{env_name}" test environment')
        except Exception as e:
            logger.error(f'🧪❌ failed to stop all test modules in "{env_name}" test environment. {e}')

    def execute_all_test_environments(self):
        try:
            test_environments = self.get_test_environments()
            if len(test_environments) > 0:
                for test_env_name in test_environments.keys():
                    logger.info(f'🧐🏃🥱 executing test environment "{test_env_name}". please wait...')
                    self.execute_all_test_modules_in_test_env(test_env_name)
                    logger.info(f'🧐🧍✔️ completed executing test environment "{test_env_name}"')
            else:
                logger.warning('🧐⚠️ Zero test environments found in configuration')
        except Exception as e:
            logger.error(f'🧐❌ failed to execute all test environments. {e}')

    def stop_all_test_environments(self):
        try:
            test_environments = self.get_test_environments()
            if len(test_environments) > 0:
                for test_env_name in test_environments.keys():
                    logger.info(f'🧐⏹️🥱 stopping test environment "{test_env_name}" execution. please wait...')
                    self.stop_all_test_modules_in_test_env(test_env_name)
                    logger.info(f'🧐🧍✔️ completed stopping test environment "{test_env_name}"')
            else:
                logger.warning('🧐⚠️ Zero test environments found in configuration')
        except Exception as e:
            logger.error(f'🧐❌ failed to stop all test environments. {e}')

    def add_database(self, database_file: str, database_channel: int, database_network: Union[str, None]=None) -> bool:
        try:
            if self.app.measurement.running:
                logger.warning("⚠️ Cannot add database while measurement is running. Please stop the measurement first.")
                return False
            else:
                databases = Databases(self.com_object.GeneralSetup.DatabaseSetup.Databases)
                databases_info = {databases.item(index).full_name: databases.item(index) for index in range(1, databases.count + 1)}
                if database_file in databases_info.keys():
                    logger.warning(f'⚠️ database "{database_file}" already added')
                    return False
                else:
                    if database_network:
                        database = databases.add_network(database_file, database_network)
                    else:
                        database = databases.add(database_file)
                    wait(0.5)
                    database.channel = database_channel
                    wait(0.5)
                    logger.info(f'📢 database "{database_file}" added successfully to channel {database_channel}')
                    return True
        except Exception as e:
            logger.error(f"❌ Error adding database '{database_file}': {e}")
            return False

    def remove_database(self, database_file: str, database_channel: int) -> bool:
        try:
            if self.app.measurement.running:
                logger.warning("⚠️ Cannot remove database while measurement is running. Please stop the measurement first.")
                return False
            else:
                databases = Databases(self.com_object.GeneralSetup.DatabaseSetup.Databases)
                databases_info = {databases.item(index).full_name: databases.item(index) for index in range(1, databases.count + 1)}
                if database_file not in databases_info.keys():
                    logger.warning(f'⚠️ database "{database_file}" not available to remove')
                    return False
                else:
                    for index in range(1, databases.count + 1):
                        database = databases.item(index)
                        if (database.full_name == database_file) and (database.channel == database_channel):
                            databases.remove(index)
                            wait(1)
                            logger.info(f'📢 database "{database_file}" removed from channel "{database_channel}"')
                            return True
                    logger.warning(f'⚠️ unable to remove database "{database_file}" from channel "{database_channel}"')
                    return False
        except Exception as e:
            logger.error(f"❌ Error removing database '{database_file}': {e}")
            return False

    def get_mode(self) -> int:
        logger.info(f"⚙️ CANoe Configuration mode = ({self.mode} - {'Offline mode' if self.mode == 1 else 'Online mode'})")
        return self.mode

    def set_mode(self, type: int) -> bool:
        try:
            if type in [0, 1]:
                self.mode = type
                logger.info(f"⚙️ CANoe Configuration mode set to ({type} - {'Offline mode' if type == 1 else 'Online mode'})")
                return True
            else:
                logger.warning("⚠️ Invalid mode type. Use 0 for Offline mode and 1 for Online mode.")
                return False
        except Exception as e:
            logger.error(f"❌ Error setting CANoe Configuration mode: {e}")
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
                        logger.info(f'📢 logging block {full_name} started')
                    else:
                        logging_block.trigger.stop()
                        logger.info(f'📢 logging block {full_name} stopped')
                    return True
            logger.warning(f'⚠️ logging block {full_name} not found.')
            return False
        except Exception as e:
            logger.error(f"❌ Error starting/stopping logging block {full_name}. {e}")

    def set_configuration_modified(self, modified: bool) -> None:
        self.modified = modified
