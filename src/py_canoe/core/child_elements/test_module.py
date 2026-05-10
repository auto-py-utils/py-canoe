import win32com.client

from py_canoe.helpers.common import logger, wait, DoEventsUntil

TEST_MODULE_START_EVENT_TIMEOUT = 5  # seconds


class TestModuleEvents:
    """test module events object."""
    def __init__(self):
        self.TM_STARTED = False
        self.TM_PAUSED = False
        self.TM_STOPPED = False
        self.TM_STOP_REASON = -1
        self.VALUE_TABLE_STOP_REASON = {
            0: "TestModuleEnd: The test module was executed completely",
            1: "UserAbortion: The test module was stopped by the user",
            2: "GeneralError: The test module was stopped by measurement stop"
        }
        self.TM_REPORT_GENERATED = False
        self.TEST_REPORT_INFORMATION = dict()
        self.TC_FAIL = False

    def OnStart(self):
        self.TM_STARTED = True

    def OnPause(self):
        self.TM_PAUSED = True

    def OnStop(self, reason):
        self.TM_STOP_REASON = reason
        self.TM_STOPPED = True

    def OnReportGenerated(self, success, sourceFullName, generatedFullName):
        self.TEST_REPORT_INFORMATION = {
            "success": success,
            "source_full_name": sourceFullName,
            "generated_full_name": generatedFullName
        }
        self.TM_REPORT_GENERATED = True

    def OnVerdictFail(self):
        self.TC_FAIL = True


class TestModule:
    """The TestModule object represents a test module in CANoe's test setup."""

    def __init__(self, com_object):
        self.com_object = win32com.client.Dispatch(com_object)
        self.test_module_events: TestModuleEvents = win32com.client.WithEvents(self.com_object, TestModuleEvents)
        self.VALUE_TABLE_VERDICT = {
            0: "NotAvailable",
            1: "Passed",
            2: "Failed",
            3: "None",
            4: "Inconclusive",
            5: "ErrorInTestSystem"
        }
        self.VALUE_TABLE_VERDICT_IMPACT = {
            0: "NoImpact",
            1: "EndTestCaseOnFail",
            2: "EndTestModuleOnFail"
        }

    @property
    def name(self) -> str:
        return self.com_object.Name

    @property
    def full_name(self) -> str:
        return self.com_object.FullName

    @property
    def path(self) -> str:
        return self.com_object.Path

    @property
    def number_of_executions(self) -> int:
        return self.com_object.NumberOfExecutions

    @number_of_executions.setter
    def number_of_executions(self, value: int):
        self.com_object.NumberOfExecutions = value

    @property
    def randomize_each_cycle(self) -> bool:
        return self.com_object.RandomizeEachCycle

    @randomize_each_cycle.setter
    def randomize_each_cycle(self, value: bool):
        self.com_object.RandomizeEachCycle = value

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
    def start_on_measurement(self) -> bool:
        return self.com_object.StartOnMeasurement

    @start_on_measurement.setter
    def start_on_measurement(self, value: bool):
        self.com_object.StartOnMeasurement = value

    @property
    def start_on_sys_var(self) -> str:
        return self.com_object.StartOnSysVar

    @start_on_sys_var.setter
    def start_on_sys_var(self, value: str):
        self.com_object.StartOnSysVar = value

    @property
    def test_cases_executed_in_random_order(self) -> bool:
        return self.com_object.TestCasesExecutedInRandomOrder

    @test_cases_executed_in_random_order.setter
    def test_cases_executed_in_random_order(self, value: bool):
        self.com_object.TestCasesExecutedInRandomOrder = value

    @property
    def test_state_sys_var(self) -> str:
        return self.com_object.TestStateSysVar

    @test_state_sys_var.setter
    def test_state_sys_var(self, value: str):
        self.com_object.TestStateSysVar = value

    @property
    def verdict(self) -> int:
        return self.com_object.Verdict

    @property
    def verdict_impact(self) -> int:
        return self.com_object.VerdictImpact

    @verdict_impact.setter
    def verdict_impact(self, value: int):
        self.com_object.VerdictImpact = value

    def _init_tm_event_variables(self):
        self.test_module_events.TM_STARTED = False
        self.test_module_events.TM_PAUSED = False
        self.test_module_events.TM_STOPPED = False
        self.test_module_events.TM_STOP_REASON = -1
        self.test_module_events.TM_REPORT_GENERATED = False
        self.test_module_events.TEST_REPORT_INFORMATION = dict()
        self.test_module_events.TC_FAIL = False

    def start(self):
        self._init_tm_event_variables()
        self.com_object.Start()
        status = DoEventsUntil(lambda: self.test_module_events.TM_STARTED, TEST_MODULE_START_EVENT_TIMEOUT, "Test Module Start")
        if status:
            logger.info(f'🧪🏃 started executing test module ({self.name})...')

    def wait_for_completion(self) -> bool:
        return_value = False
        if self.test_module_events.TM_STARTED:
            logger.info(f'🧪🥱 waiting for test module ({self.name}) to complete...')
            while not self.test_module_events.TM_STOPPED:
                wait(0.01)
            logger.info(f'🧪🧍 test module ({self.name}) execution completed with stop reason 👉 {self.test_module_events.VALUE_TABLE_STOP_REASON[self.test_module_events.TM_STOP_REASON]}')
            return_value = True
        else:
            logger.warning(f'🧪⚠️ Test Module ({self.name}) is not started. Start the Test Module first.')
        return return_value

    def pause(self) -> bool:
        if self.test_module_events.TM_STARTED:
            self.com_object.Pause()
            logger.info(f'🧪🥱 pausing test module ({self.name}). please wait...')
            while not self.test_module_events.TM_PAUSED:
                wait(0.01)
            logger.info(f'🧪⏸️ paused test module ({self.name}).')
            return True
        else:
            logger.warning(f'🧪⚠️ Test Module ({self.name}) is not started. Start the Test Module first.')
            return False

    def resume(self) -> None:
        self.com_object.Resume()

    def stop(self) -> bool:
        if self.test_module_events.TM_STARTED:
            self.com_object.Stop()
            logger.info(f'🧪🥱 stopping test module ({self.name}). please wait...')
            while not self.test_module_events.TM_STOPPED:
                wait(0.01)
            logger.info(f'🧪⏹️ stopped test module ({self.name}).')
            return True
        else:
            logger.warning(f'🧪⚠️ Test Module ({self.name}) is not started. Start the Test Module first.')
            return False

    def reload(self) -> None:
        self.com_object.Reload()

    def set_execution_time(self, days: int, hours: int, minutes: int):
        self.com_object.SetExecutionTime(days, hours, minutes)
