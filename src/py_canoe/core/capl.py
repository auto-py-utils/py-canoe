from typing import Union

from py_canoe.helpers.common import logger
from py_canoe.helpers.common import wait

from py_canoe.core.child_elements.capl_function import CaplFunction
from py_canoe.core.child_elements.compile_result import CompileResult


class Capl:
    """
    The CAPL object allows to compile all nodes (CAPL, .NET, XML) in the configuration. Additionally it represents the CAPL functions available in the CAPL programs.
    Please note that only user-defined CAPL functions can be accessed.
    """
    def __init__(self, app):
        self.com_object = app.com_object.CAPL
        self.capl_function_objects = lambda: app.measurement.measurement_events.CAPL_FUNCTION_OBJECTS

    @property
    def compile_result(self) -> 'CompileResult':
        return CompileResult(self.com_object.CompileResult)

    def compile(self, wait_time: Union[int, float] = 5) -> Union['CompileResult', None]:
        try:
            self.com_object.Compile()
            wait(wait_time)
            compile_result = self.compile_result
            logger.info(f'compiled all CAPL nodes. result={compile_result.result}')
            return compile_result
        except Exception as e:
            logger.error(f"Error compiling CAPL nodes: {e}")
            return None

    def get_function(self, name: str) -> Union['CaplFunction', None]:
        if name in self.capl_function_objects():
            return self.capl_function_objects()[name]
        else:
            logger.warning(f'CAPL function "{name}" not found/registered.')
            return None

    def call_capl_function(self, name: str, *arguments) -> bool:
        try:
            capl_function = self.get_function(name)
            if capl_function:
                if len(arguments) != capl_function.parameter_count:
                    logger.warning(f"Not enough arguments provided for CAPL function '{name}'.")
                    return False
                else:
                    if len(arguments) > 0:
                        capl_function.call(*arguments)
                    else:
                        capl_function.call()
                    return True
            else:
                logger.warning(f"CAPL function '{name}' not found.")
                return False
        except Exception as e:
            logger.error(f"Error calling CAPL function '{name}': {e}")
            return False
