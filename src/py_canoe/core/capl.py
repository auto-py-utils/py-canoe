from typing import Union, TYPE_CHECKING

from py_canoe.helpers.common import logger
from py_canoe.helpers.common import wait
if TYPE_CHECKING:
    from py_canoe.core.application import Application
from py_canoe.core.child_elements.capl_function import CaplFunction
from py_canoe.core.child_elements.compile_result import CompileResult


class Capl:
    """
    The CAPL object allows to compile all nodes (CAPL, .NET, XML) in the configuration. Additionally it represents the CAPL functions available in the CAPL programs.
    Please note that only user-defined CAPL functions can be accessed.
    """
    def __init__(self, app: 'Application'):
        self.com_object = app.com_object.CAPL
        self.capl_function_objects = lambda: app.measurement.measurement_events.CAPL_FUNCTION_OBJECTS

    @property
    def compile_result(self) -> 'CompileResult':
        """Return the result of the last CAPL compilation as a CompileResult object."""
        return CompileResult(self.com_object.CompileResult)

    def compile(self, wait_time: Union[int, float] = 5) -> Union['CompileResult', None]:
        """Compile all CAPL nodes in the configuration and return the result as a CompileResult object. Optionally, specify a wait time (in seconds) for the compilation to complete."""
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
        """Get CAPL function object by name. Returns a CaplFunction object if found, or None if not found."""
        if name in self.capl_function_objects():
            return self.capl_function_objects()[name]
        else:
            logger.warning(f'CAPL function "{name}" not found/registered.')
            return None

    def call_capl_function(self, name: str, *arguments) -> bool:
        """Call a CAPL function by name with the provided arguments. Returns True if the function was called successfully, False otherwise."""
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
