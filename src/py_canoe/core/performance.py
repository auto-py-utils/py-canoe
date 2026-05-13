from py_canoe.helpers.common import logger


class Performance:
    """
    The Performance object allows setting or returning parameters that influence the performance on multicore processors.
    """
    def __init__(self, app):
        self.app = app
        self.com_object = self.app.com_object.Performance

    @property
    def max_num_measurement_setup_threads(self) -> int:
        return self.com_object.MaxNumMeasurementSetupThreads

    @max_num_measurement_setup_threads.setter
    def max_num_measurement_setup_threads(self, num: int):
        if not self.app.get_measurement_running_status():
            self.com_object.MaxNumMeasurementSetupThreads = num
        else:
            logger.warning("Cannot set MaxNumMeasurementSetupThreads while measurement is running.")
