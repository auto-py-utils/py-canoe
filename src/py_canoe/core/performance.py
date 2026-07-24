from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from py_canoe.core.application import Application
from py_canoe.helpers.common import logger


class Performance:
    """
    The Performance object allows setting or returning parameters that influence the performance on multicore processors.
    """
    def __init__(self, app: 'Application'):
        self.app = app
        self.com_object = self.app.com_object.Performance

    @property
    def max_num_measurement_setup_threads(self) -> int:
        """Return the maximum number of measurement setup threads that can be used for measurement setup."""
        return self.com_object.MaxNumMeasurementSetupThreads

    @max_num_measurement_setup_threads.setter
    def max_num_measurement_setup_threads(self, num: int):
        """Set the maximum number of measurement setup threads that can be used for measurement setup."""
        if not self.app.get_measurement_running_status():
            self.com_object.MaxNumMeasurementSetupThreads = num
        else:
            logger.warning("Cannot set MaxNumMeasurementSetupThreads while measurement is running.")
