import os

from py_canoe.core.child_elements.test_module import TestModule
from py_canoe.helpers.common import logger


class TestModules:
    def __init__(self, com_object) -> None:
        self.com_object = com_object

    @property
    def count(self) -> int:
        return self.com_object.Count

    def add(self, full_name: str) -> 'TestModule':
        """Adds a test module to a test environment or a test setup folder.

        The path can be absolute or relative to the current CANoe configuration.

        Args:
            full_name: The path of the CAPL program (.can) or the XML test description
                       (.tse/.stse/.vxt) for the test module. This must be a valid file
                       path, not a module name.

        Returns:
            The newly created TestModule object.

        Raises:
            FileNotFoundError: If the given absolute path does not exist.
        """
        # Fail early with a clear message instead of a cryptic COM
        # 'File not found!' error.
        if not os.path.isabs(full_name):
            logger.warning(
                f'TestModules.add: "{full_name}" is not an absolute path. '
                f'The path is resolved relative to the current CANoe configuration.'
            )
        elif not os.path.exists(full_name):
            raise FileNotFoundError(
                f'TestModules.add: file not found: "{full_name}". '
                f'Pass the full path to a CAPL program (.can) or XML test description '
                f'(.tse/.stse/.vxt) file, not a module name.'
            )
        module = TestModule(self.com_object.Add(full_name))
        logger.info(f'TestModules: added test module from "{full_name}" as "{module.name}".')
        return module

    def remove(self, index: int, prompt_user=False) -> None:
        self.com_object.Remove(index, prompt_user)
        logger.info(f'TestModules: removed test module at index/name "{index}".')

    def fetch_test_modules(self) -> dict['str': 'TestModule']:
        test_modules = dict()
        for index in range(1, self.count + 1):
            tm_inst = TestModule(self.com_object.Item(index))
            test_modules[tm_inst.name] = tm_inst
        return test_modules
