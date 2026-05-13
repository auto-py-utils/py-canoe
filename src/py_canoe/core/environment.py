# TODO: complete implementation of the Environment class
from typing import Union

from py_canoe.helpers.common import logger
from py_canoe.core.child_elements.environment_group import EnvironmentGroup
from py_canoe.core.child_elements.environment_info import EnvironmentInfo
from py_canoe.core.child_elements.environment_variable import EnvironmentVariable


class Environment:
    """
    The Environment object represents the environment variables.
    """
    def __init__(self, app):
        self.com_object = app.com_object.Environment

    def create_group(self):
        return EnvironmentGroup(self.com_object.CreateGroup())

    def create_info(self) -> 'EnvironmentInfo':
        return EnvironmentInfo(self.com_object.CreateInfo())

    def get_variable(self, name: str) -> 'EnvironmentVariable':
        return EnvironmentVariable(self.com_object.GetVariable(name))

    def get_variables(self, vars: list[list[Union[str, int, float]]]) -> list:
        return self.com_object.GetVariables(vars)

    def set_variables(self, vars: dict):
        self.com_object.SetVariables(vars)

    def get_environment_variable_value(self, env_var_name: str) -> Union[int, float, str, tuple, None]:
        var_value = None
        try:
            variable = self.get_variable(env_var_name)
            var_value = variable.value if variable.type != 3 else tuple(variable.value)
            logger.info(f'environment variable({env_var_name}) value = {var_value}')
        except Exception as e:
            logger.error(f"Failed to get environment variable '{env_var_name}': {e}")
        finally:
            return var_value

    def set_environment_variable_value(self, env_var_name: str, value: Union[int, float, str, tuple]) -> bool:
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
