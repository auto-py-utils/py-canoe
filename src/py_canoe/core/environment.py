# TODO: complete implementation of the Environment class
from typing import Union, TYPE_CHECKING
if TYPE_CHECKING:
    from py_canoe.core.application import Application
from py_canoe.helpers.common import logger
from py_canoe.core.child_elements.environment_group import EnvironmentGroup
from py_canoe.core.child_elements.environment_info import EnvironmentInfo
from py_canoe.core.child_elements.environment_variable import EnvironmentVariable


class Environment:
    """
    The Environment object represents the environment variables.
    """
    def __init__(self, app: 'Application'):
        self.com_object = app.com_object.Environment

    def create_group(self):
        """Create a new environment group and return it as an EnvironmentGroup object."""
        return EnvironmentGroup(self.com_object.CreateGroup())

    def create_info(self) -> 'EnvironmentInfo':
        """Create a new environment info object and return it as an EnvironmentInfo object."""
        return EnvironmentInfo(self.com_object.CreateInfo())

    def get_variable(self, name: str) -> 'EnvironmentVariable':
        """Get an environment variable by name and return it as an EnvironmentVariable object."""
        return EnvironmentVariable(self.com_object.GetVariable(name))

    def get_variables(self, vars: list[list[Union[str, int, float]]]) -> list:
        """Get the values of multiple environment variables specified in a list of lists, where each inner list contains the variable name and its type. Returns a list of variable values."""
        return self.com_object.GetVariables(vars)

    def set_variables(self, vars: dict):
        """Set the values of multiple environment variables specified in a dictionary, where keys are variable names and values are the corresponding values to set."""
        self.com_object.SetVariables(vars)

    def get_environment_variable_value(self, env_var_name: str) -> Union[int, float, str, tuple, None]:
        """Get the value of an environment variable by name. Returns the value as an integer, float, string, or tuple, or None if an error occurs."""
        try:
            variable = self.get_variable(env_var_name)
            var_value = variable.value if variable.type != 3 else tuple(variable.value)
            logger.info(f'environment variable({env_var_name}) value = {var_value}')
            return var_value
        except Exception as e:
            logger.error(f"Failed to get environment variable '{env_var_name}': {e}")
            return None

    def set_environment_variable_value(self, env_var_name: str, value: Union[int, float, str, tuple]) -> bool:
        """Set the value of an environment variable by name. The value can be an integer, float, string, or tuple. Returns True if successful, False otherwise."""
        try:
            variable = self.get_variable(env_var_name)
            if variable.type == 0:
                converted_value = int(value)
            elif variable.type == 1:
                converted_value = float(value)
            elif variable.type == 2:
                converted_value = str(value)
            else:
                converted_value = tuple(value)
            variable.value = converted_value
            logger.info(f'environment variable({env_var_name}) set to {converted_value}')
            return True
        except Exception as e:
            logger.error(f"Failed to set environment variable '{env_var_name}': {e}")
            return False
