from typing import Union

from py_canoe.helpers.common import logger
from py_canoe.core.child_elements.namespaces import Namespaces
from py_canoe.core.child_elements.variables import Variables
from py_canoe.core.child_elements.variables_files import VariablesFiles
from py_canoe.core.child_elements.variable import Variable
from py_canoe.exceptions import PyCanoeError, NamespaceNotFoundError


class System:
    """
    The System object represents the system of the CANoe application.
    The System object offers access to the namespaces for data exchange with external applications.
    """
    def __init__(self, app):
        self.com_object = app.com_object.System

    @property
    def namespaces(self) -> Namespaces:
        return Namespaces(self.com_object.Namespaces)

    @property
    def variables_files(self) -> VariablesFiles:
        return VariablesFiles(self.com_object.VariablesFiles)


    def add_variable(self, sys_var_name: str, value: Union[int, float, str], read_only: bool = False) -> Union[object, None]:
        new_var_com_obj = None
        try:
            parts = sys_var_name.split('::')
            if len(parts) < 2:
                logger.error(f"Invalid system variable name '{sys_var_name}'. Must be in 'namespace::variable' format.")
                return None
            namespace = '::'.join(parts[:-1])
            variable_name = parts[-1]
            try:
                namespace_obj = self.com_object.Namespaces(namespace)
            except Exception:
                logger.info(f"namespace '{namespace}' not present. Creating namespace...")
                namespaces_obj = self.com_object.Namespaces
                namespace_obj = namespaces_obj.Add(namespace)
                logger.info(f"Created new namespace: {namespace}")
            variables_obj = namespace_obj.Variables
            if read_only:
                new_var_com_obj = variables_obj.Add(variable_name, value)
            else:
                new_var_com_obj = variables_obj.AddWriteable(variable_name, value)
            logger.info(f"System Variable '{sys_var_name}' defined successfully with value: {value}")
            return new_var_com_obj
        except Exception as e:
            logger.error(f"Error defining System Variable '{sys_var_name}': {e}")
            return None

    def remove_variable(self, sys_var_name: str) -> bool:
        try:
            parts = sys_var_name.split('::')
            if len(parts) < 2:
                logger.error(f"Invalid system variable name '{sys_var_name}'. Must be in 'namespace::variable' format.")
                return None
            namespace = '::'.join(parts[:-1])
            variable_name = parts[-1]
            namespace_obj = self.com_object.Namespaces(namespace)
            variables_obj = namespace_obj.Variables
            for i in range(1, variables_obj.Count + 1):
                variable_obj = variables_obj.Item(i)
                if variable_obj.Name == variable_name:
                    variables_obj.Remove(i)
                    logger.info(f"System Variable '{sys_var_name}' removed successfully.")
                    return True
            logger.info(f"System Variable '{sys_var_name}' not found.")
            return False
        except Exception as e:
            logger.error(f"Error removing System Variable '{sys_var_name}': {e}")
            return False

    def get_variable_value(self, sys_var_name: str, return_symbolic_name=False) -> Union[int, float, str, None]:
        try:
            parts = sys_var_name.split('::')
            if len(parts) < 2:
                logger.error(f"Invalid system variable name '{sys_var_name}'. Must be in 'namespace::variable' format.")
                return None
            namespace = '::'.join(parts[:-1])
            variable_name = parts[-1]
            namespace_obj = self.com_object.Namespaces(namespace)
            variable_obj = Variable(namespace_obj.Variables(variable_name))
            value = variable_obj.get_value()
            if return_symbolic_name:
                symbolic_value = variable_obj.get_symbolic_value_name(value)
                logger.info(f"System Variable '{sys_var_name}' symbolic value: {symbolic_value}")
                return symbolic_value
            logger.info(f"System Variable '{sys_var_name}' value: {value}")
            return value
        except Exception as e:
            logger.error(f"Error retrieving System Variable '{sys_var_name}': {e}")
            return None

    def set_variable_value(self, sys_var_name: str, value: Union[int, float, str], timeout: Union[int, float] = 1) -> bool:
        try:
            parts = sys_var_name.split('::')
            if len(parts) < 2:
                logger.error(f"Invalid system variable name '{sys_var_name}'. Must be in 'namespace::variable' format.")
                return False
            namespace = '::'.join(parts[:-1])
            variable_name = parts[-1]
            namespace_obj = self.com_object.Namespaces(namespace)
            variable_obj = Variable(namespace_obj.Variables(variable_name))
            var_type = type(variable_obj.get_value())
            try:
                converted_value = var_type(value)
            except Exception:
                logger.error(f"Could not convert value '{value}' to type {var_type.__name__} for '{sys_var_name}'")
                return False
            status = variable_obj.set_value(converted_value, timeout)
            return status
        except Exception as e:
            logger.error(f"Error setting System Variable '{sys_var_name}': {e}")
            return False

    def set_variable_array_values(self, sys_var_name: str, value: tuple, index: int = 0, timeout: Union[int, float] = 1) -> bool:
        try:
            parts = sys_var_name.split('::')
            if len(parts) < 2:
                logger.error(f"Invalid system variable name '{sys_var_name}'. Must be in 'namespace::variable' format.")
                return False
            namespace = '::'.join(parts[:-1])
            variable_name = parts[-1]
            namespace_obj = self.com_object.Namespaces(namespace)
            variable_obj = Variable(namespace_obj.Variables(variable_name))
            arr = list(variable_obj.get_value())
            if index < 0 or index + len(value) > len(arr):
                logger.error(f"Not enough space in System Variable Array '{sys_var_name}' to set values.")
                return False
            value_type = type(arr[0]) if arr else type(value[0])
            arr[index:index + len(value)] = [value_type(v) for v in value]
            status = variable_obj.set_value(tuple(arr), timeout)
            return status
        except Exception as e:
            logger.error(f"Error setting System Variable Array '{sys_var_name}': {e}")
            return False

    def get_namespaces(self) -> dict[str, "Namespace"] | None:
        try:
            namespaces_dict = {}
            namespaces = self.namespaces
            for index in range(1, namespaces.count + 1):
                namespace = namespaces.item(index)
                namespaces_dict[namespace.name] = namespace
            logger.info(f"total {namespaces.count} system root namespaces found.")
            return namespaces_dict
        except Exception as e:
            logger.error(f"Error getting system namespaces: {e}")
            return None

    def get_all_namespace_names(self) -> list[str]:
        try:
            names = [ns.name for ns in self.namespaces.fetch_all()]
        except Exception as e:
            raise PyCanoeError(f"Failed to enumerate namespaces: {e}") from e
        logger.info(f'{len(names)} system variable namespace(s) found')
        return names

    def get_all_variables_in_namespace(self, namespace_name: str) -> list[dict]:
        try:
            ns_com = self.com_object.Namespaces(namespace_name)
        except Exception as e:
            raise NamespaceNotFoundError(f"Namespace '{namespace_name}' not found: {e}") from e
        try:
            variables_obj = Variables(ns_com.Variables)
            result = []
            for var in variables_obj.fetch_all():
                result.append({
                    "name": var.name,
                    "value": var.get_value(),
                    "full_name": var.full_name,
                })
            logger.info(f"{len(result)} variable(s) found in '{namespace_name}'")
            return result
        except Exception as e:
            raise PyCanoeError(f"Failed to enumerate variables in '{namespace_name}': {e}") from e

    def get_variables_files(self) -> dict[str, "VariablesFile"] | None:
        try:
            variables_files_dict = {}
            variables_files = self.variables_files
            for index in range(1, variables_files.count + 1):
                variables_file = variables_files.item(index)
                variables_files_dict[variables_file.full_name] = variables_file
            logger.info(f"total {variables_files.count} system variables files found.")
            return variables_files_dict
        except Exception as e:
            logger.error(f"Error getting system variables files: {e}")
            return None
