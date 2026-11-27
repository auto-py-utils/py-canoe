from py_canoe.core.com_session import dispatch_com_object


class TestConfigurationSettings:
    """The TestConfigurationSettings object represents the settings of a test configuration."""

    def __init__(self, com_object):
        self.com_object = dispatch_com_object(com_object)

    def __getattr__(self, item):
        return getattr(self.com_object, item)

    # --- Properties ---

    @property
    def asynchronous_check_evaluation_mode(self) -> int:
        return self.com_object.AsynchronousCheckEvaluationMode

    @asynchronous_check_evaluation_mode.setter
    def asynchronous_check_evaluation_mode(self, value: int):
        self.com_object.AsynchronousCheckEvaluationMode = value

    @property
    def debug_mode(self) -> int:
        return self.com_object.DebugMode

    @debug_mode.setter
    def debug_mode(self, value: int):
        self.com_object.DebugMode = value

    @property
    def debug_mode_pausing_verdict(self) -> int:
        return self.com_object.DebugModePausingVerdict

    @debug_mode_pausing_verdict.setter
    def debug_mode_pausing_verdict(self, value: int):
        self.com_object.DebugModePausingVerdict = value

    @property
    def execution_mode(self) -> int:
        return self.com_object.ExecutionMode

    @execution_mode.setter
    def execution_mode(self, value: int):
        self.com_object.ExecutionMode = value

    @property
    def ignore_break_on_error_in_test_system(self) -> bool:
        return self.com_object.IgnoreBreakOnErrorInTestSystem

    @ignore_break_on_error_in_test_system.setter
    def ignore_break_on_error_in_test_system(self, value: bool):
        self.com_object.IgnoreBreakOnErrorInTestSystem = value

    @property
    def ignore_break_on_fail(self) -> bool:
        return self.com_object.IgnoreBreakOnFail

    @ignore_break_on_fail.setter
    def ignore_break_on_fail(self, value: bool):
        self.com_object.IgnoreBreakOnFail = value

    @property
    def number_of_executions(self) -> int:
        return self.com_object.NumberOfExecutions

    @number_of_executions.setter
    def number_of_executions(self, value: int):
        self.com_object.NumberOfExecutions = value

    @property
    def randomize_execution_mode(self) -> bool:
        return self.com_object.RandomizeExecutionMode

    @randomize_execution_mode.setter
    def randomize_execution_mode(self, value: bool):
        self.com_object.RandomizeExecutionMode = value

    @property
    def start_on_env_var(self) -> str:
        return self.com_object.StartOnEnvVar

    @start_on_env_var.setter
    def start_on_env_var(self, value: str):
        self.com_object.StartOnEnvVar = value

    @property
    def start_on_key(self) -> str:
        return self.com_object.StartOnKey

    @start_on_key.setter
    def start_on_key(self, value: str):
        self.com_object.StartOnKey = value

    @property
    def start_on_measurement(self) -> str:
        return self.com_object.StartOnMeasurement

    @start_on_measurement.setter
    def start_on_measurement(self, value: str):
        self.com_object.StartOnMeasurement = value

    @property
    def start_on_sys_var(self) -> str:
        return self.com_object.StartOnSysVar

    @start_on_sys_var.setter
    def start_on_sys_var(self, value: str):
        self.com_object.StartOnSysVar = value

    @property
    def stop_on_env_var(self) -> str:
        return self.com_object.StopOnEnvVar

    @stop_on_env_var.setter
    def stop_on_env_var(self, value: str):
        self.com_object.StopOnEnvVar = value

    @property
    def stop_on_key(self) -> str:
        return self.com_object.StopOnKey

    @stop_on_key.setter
    def stop_on_key(self, value: str):
        self.com_object.StopOnKey = value

    @property
    def stop_on_sys_var(self) -> str:
        return self.com_object.StopOnSysVar

    @stop_on_sys_var.setter
    def stop_on_sys_var(self, value: str):
        self.com_object.StopOnSysVar = value

    @property
    def verdict_impact(self) -> int:
        return self.com_object.VerdictImpact

    @verdict_impact.setter
    def verdict_impact(self, value: int):
        self.com_object.VerdictImpact = value

    # --- Methods ---

    def set_execution_time(self, days: int, hours: int, minutes: int) -> None:
        self.com_object.SetExecutionTime(days, hours, minutes)

