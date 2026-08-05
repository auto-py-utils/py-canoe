import win32com.client

from py_canoe.core.child_elements.modules import Modules
from py_canoe.core.child_elements.test_case import TestCase
from py_canoe.core.child_elements.test_libraries import TestLibraries
from py_canoe.core.child_elements.test_report import TestReport
from py_canoe.core.child_elements.test_setup_item import TestSetupItem
from py_canoe.helpers.common import logger, wait, DoEventsUntil

TEST_MODULE_START_EVENT_TIMEOUT = 5  # seconds


class TestModuleEvents:
    """test module events object."""

    __test__ = False

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
        logger.info(f"TestModuleVerdict: ({success}), sourceFullName: ({sourceFullName}), generatedFullName:({generatedFullName})")
        self.TM_REPORT_GENERATED = True

    def OnVerdictFail(self):
        self.TC_FAIL = True


class TestModule(TestSetupItem):
    """The TestModule object represents a test module in CANoe's test setup.

    Inherits from TestSetupItem.
    """

    __test__ = False

    def __init__(self, com_object):
        super().__init__(com_object)
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
        self.VALUE_TABLE_DEBUG_MODE = {
            0: "NoDebugPause",
            1: "DebugPauseAfterFailedTestCaseOrPattern",
            2: "DebugPauseAfterEachTestCaseOrPattern"
        }
        self.VALUE_TABLE_EXECUTION_MODE = {
            0: "DefinedNumberOfRepeats",
            1: "RepeatForDefinedTime",
            2: "RepeatForever"
        }
        self.VALUE_TABLE_PAUSING_MODE = {
            0: "PauseAfterTestCaseOnly",
            1: "PauseAfterTestCaseAndTestPattern"
        }

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

    # --- Additional COM properties ---

    @property
    def debug_mode(self) -> int:
        """Sets/returns the debug pause setting."""
        return self.com_object.DebugMode

    @debug_mode.setter
    def debug_mode(self, value: int) -> None:
        self.com_object.DebugMode = value

    @property
    def enabled(self) -> bool:
        """Activates/deactivates the test module."""
        return self.com_object.Enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self.com_object.Enabled = value

    @property
    def execute_repeatedly(self) -> bool:
        """Sets/returns whether the test module should be executed repeatedly."""
        return self.com_object.ExecuteRepeatedly

    @execute_repeatedly.setter
    def execute_repeatedly(self, value: bool) -> None:
        self.com_object.ExecuteRepeatedly = value

    @property
    def execution_mode(self) -> int:
        """Sets/returns how the test module is executed."""
        return self.com_object.ExecutionMode

    @execution_mode.setter
    def execution_mode(self, value: int) -> None:
        self.com_object.ExecutionMode = value

    @property
    def libraries(self) -> TestLibraries:
        """Returns the TestLibraries object of the test module.

        Represents the test case files used in XML or .NET test modules.
        """
        return TestLibraries(self.com_object.Libraries)

    @property
    def modules(self) -> Modules:
        """Returns the Modules object of the test module.

        Use ``add()`` to add node layer modules (DLL), assemblies (DLL),
        .NET source files (CS) or CAPL source files (CAN) to the test module.
        """
        return Modules(self.com_object.Modules)

    @property
    def pausing_mode(self) -> int:
        """Sets/returns whether pausing occurs after test cases or test patterns."""
        return self.com_object.PausingMode

    @pausing_mode.setter
    def pausing_mode(self, value: int) -> None:
        self.com_object.PausingMode = value

    @property
    def report(self) -> TestReport:
        """Returns a TestReport object of the test module.

        The wrapper (and its COM event sink) is cached after first access.
        """
        if getattr(self, "_report", None) is None:
            self._report = TestReport(self.com_object.Report)
        return self._report

    @property
    def sequence_ex(self):
        """Returns the TestSequenceEx object of the test module."""
        return self.com_object.SequenceEx

    @property
    def specification_style_sheet(self) -> str:
        """Sets/returns the XSLT stylesheet for converting the XML test description."""
        return self.com_object.SpecificationStyleSheet

    @specification_style_sheet.setter
    def specification_style_sheet(self, value: str) -> None:
        self.com_object.SpecificationStyleSheet = value

    @property
    def tcp_ip_stack_setting(self):
        """Returns the TcpIpStackSetting object of the test module."""
        return self.com_object.TcpIpStackSetting

    @property
    def test_variant(self) -> str:
        """Returns/activates the current test variant (XML test modules only)."""
        return self.com_object.TestVariant

    @test_variant.setter
    def test_variant(self, value: str) -> None:
        self.com_object.TestVariant = value

    def _init_tm_event_variables(self):
        self.test_module_events.TM_STARTED = False
        self.test_module_events.TM_PAUSED = False
        self.test_module_events.TM_STOPPED = False
        self.test_module_events.TM_STOP_REASON = -1
        self.test_module_events.TM_REPORT_GENERATED = False
        self.test_module_events.TEST_REPORT_INFORMATION = dict()
        self.test_module_events.TC_FAIL = False

    def start(self) -> bool:
        """Starts the test module and waits for the OnStart event.

        Returns:
            bool: True if the test module started successfully, False otherwise.
        """
        self._init_tm_event_variables()
        self.com_object.Start()
        status = DoEventsUntil(lambda: self.test_module_events.TM_STARTED, TEST_MODULE_START_EVENT_TIMEOUT, "Test Module Start")
        if status:
            logger.info(f'started executing test module ({self.name})...')
        else:
            logger.warning(f'Test Module ({self.name}) did not start within {TEST_MODULE_START_EVENT_TIMEOUT}s.')
        return status

    def wait_for_completion(self, timeout: int = None) -> bool:
        """Waits for the test module to complete execution.

        Args:
            timeout: Maximum time in seconds to wait. If None, waits indefinitely.

        Returns:
            bool: True if the test module completed, False if it was not started
                  or timed out.
        """
        if not self.test_module_events.TM_STARTED:
            logger.warning(f'Test Module ({self.name}) is not started. Start the Test Module first.')
            return False

        logger.info(f'waiting for test module ({self.name}) to complete...')
        if timeout is None:
            while not self.test_module_events.TM_STOPPED:
                wait(0.01)
        else:
            completed = DoEventsUntil(
                lambda: self.test_module_events.TM_STOPPED,
                timeout,
                f"Test Module ({self.name}) Completion"
            )
            if not completed:
                logger.warning(f'Test Module ({self.name}) did not complete within {timeout}s.')
                return False

        logger.info(
            f'test module ({self.name}) execution completed with stop reason '
            f'{self.test_module_events.VALUE_TABLE_STOP_REASON[self.test_module_events.TM_STOP_REASON]}'
        )
        return True

    def pause(self, timeout: int = None) -> bool:
        """Pauses the test module and waits for the OnPause event.

        Args:
            timeout: Maximum time in seconds to wait. If None, waits indefinitely.

        Returns:
            bool: True if the test module paused, False if it was not started or timed out.
        """
        if not self.test_module_events.TM_STARTED:
            logger.warning(f'Test Module ({self.name}) is not started. Start the Test Module first.')
            return False

        self.com_object.Pause()
        logger.info(f'pausing test module ({self.name}). please wait...')
        if timeout is None:
            while not self.test_module_events.TM_PAUSED:
                wait(0.01)
        else:
            paused = DoEventsUntil(
                lambda: self.test_module_events.TM_PAUSED,
                timeout,
                f"Test Module ({self.name}) Pause"
            )
            if not paused:
                logger.warning(f'Test Module ({self.name}) did not pause within {timeout}s.')
                return False
        logger.info(f'paused test module ({self.name}).')
        return True

    def resume(self) -> bool:
        """Resumes the test module execution from the point at which it was paused.

        Returns:
            bool: True if the test module was started and resume was issued, False otherwise.
        """
        if self.test_module_events.TM_STARTED:
            self.com_object.Resume()
            logger.info(f'resumed test module ({self.name}).')
            return True
        else:
            logger.warning(f'Test Module ({self.name}) is not started. Start the Test Module first.')
            return False

    def stop(self, timeout: int = None) -> bool:
        """Stops the test module and waits for the OnStop event.

        Args:
            timeout: Maximum time in seconds to wait. If None, waits indefinitely.

        Returns:
            bool: True if the test module stopped, False if it was not started or timed out.
        """
        if not self.test_module_events.TM_STARTED:
            logger.warning(f'Test Module ({self.name}) is not started. Start the Test Module first.')
            return False

        self.com_object.Stop()
        logger.info(f'stopping test module ({self.name}). please wait...')
        if timeout is None:
            while not self.test_module_events.TM_STOPPED:
                wait(0.01)
        else:
            stopped = DoEventsUntil(
                lambda: self.test_module_events.TM_STOPPED,
                timeout,
                f"Test Module ({self.name}) Stop"
            )
            if not stopped:
                logger.warning(f'Test Module ({self.name}) did not stop within {timeout}s.')
                return False
        logger.info(f'stopped test module ({self.name}).')
        return True

    def reload(self) -> None:
        self.com_object.Reload()

    def set_execution_time(self, days: int, hours: int, minutes: int):
        self.com_object.SetExecutionTime(days, hours, minutes)

    # --- Test Case Methods ---

    @property
    def sequence(self):
        """Returns the Sequence object of the test module.

        The Sequence contains test cases and test groups as a tree structure.
        """
        return self.com_object.Sequence

    def _collect_test_cases(self, sequence, test_cases: dict) -> dict:
        """Recursively collect all TestCase objects from a TestSequence.

        A TestSequence contains TestSequenceItem objects that can be either
        TestCase or TestGroup. TestGroups contain nested TestSequences.
        """
        for testSequenceItem in sequence:
            try:
                testGroup = win32com.client.CastTo(testSequenceItem, "ITestGroup")
                if testGroup.Sequence.Count != 0:
                    self._collect_test_cases(testGroup.Sequence, test_cases)
            except Exception as e:
                # Not a TestGroup (or group has no nested sequence): treat it
                # as a TestCase. If even that cast fails, log and skip so we
                # don't silently drop the item.
                try:
                    testCase = win32com.client.CastTo(testSequenceItem, "ITestCase")
                    tc = TestCase(testCase)
                    test_cases[tc.name] = tc
                except Exception as e2:
                    logger.error(
                        f'Failed to cast test sequence item in module '
                        f'"{self.name}" to ITestCase: {e2}'
                    )
                    continue
        return test_cases

    def get_all_test_cases(self) -> dict[str, TestCase]:
        """Returns all test cases in this test module as a dictionary.

        Recursively traverses the test sequence tree to find all test cases,
        including those nested inside test groups.

        Note: TestCase data (e.g. Verdict) does not auto-update in CANoe.
        Call this method again to get fresh data after test execution.

        Returns:
            dict[str, TestCase]: Dictionary mapping test case names to TestCase objects.

        Example:
            >>> test_cases = test_module.get_all_test_cases()
            >>> for name, tc in test_cases.items():
            ...     print(f"{name}: enabled={tc.enabled}, verdict={tc.verdict_name}")
        """
        test_cases = {}
        try:
            self._collect_test_cases(self.sequence, test_cases)
        except Exception as e:
            logger.error(f'Error fetching test cases for test module ({self.name}): {e}')
        return test_cases

    def get_test_case(self, test_case_name: str) -> TestCase | None:
        """Returns a specific test case by name.

        Args:
            test_case_name (str): The name of the test case.

        Returns:
            TestCase | None: The TestCase object if found, None otherwise.
        """
        test_cases = self.get_all_test_cases()
        if test_case_name in test_cases:
            return test_cases[test_case_name]
        else:
            logger.warning(f'Test case "{test_case_name}" not found in test module ({self.name}).')
            return None

    def get_test_case_verdict(self, test_case_name: str) -> int:
        """Returns the verdict of a specific test case.

        Args:
            test_case_name (str): The name of the test case.

        Returns:
            int: The verdict (0=NotAvailable, 1=Passed, 2=Failed, 3=None,
                 4=Inconclusive, 5=ErrorInTestSystem). Returns -1 if not found.
        """
        tc = self.get_test_case(test_case_name)
        if tc is not None:
            return tc.verdict
        return -1

    def get_test_case_enabled(self, test_case_name: str) -> bool | None:
        """Returns whether a specific test case is enabled.

        Args:
            test_case_name (str): The name of the test case.

        Returns:
            bool | None: True if enabled, False if disabled, None if not found.
        """
        tc = self.get_test_case(test_case_name)
        if tc is not None:
            return tc.enabled
        return None

    def set_test_case_enabled(self, test_case_name: str, enabled: bool) -> bool:
        """Enable or disable a specific test case.

        Note: This is only available for XML test modules.

        Args:
            test_case_name (str): The name of the test case.
            enabled (bool): True to enable, False to disable.

        Returns:
            bool: True if successful, False if the test case was not found.
        """
        tc = self.get_test_case(test_case_name)
        if tc is not None:
            tc.enabled = enabled
            logger.info(f'Test case "{test_case_name}" {"enabled" if enabled else "disabled"} in test module ({self.name}).')
            return True
        return False

    def get_all_test_case_verdicts(self) -> dict[str, dict]:
        """Returns verdict and enabled status for all test cases.

        This is a convenience method that returns a snapshot of all test cases
        with their current verdict and enabled state. Since TestCase data does
        not auto-update, call this method again to refresh after test execution.

        Returns:
            dict[str, dict]: Dictionary mapping test case names to dicts with keys:
                - "verdict" (int): The verdict value (0-5)
                - "verdict_name" (str): Human-readable verdict name
                - "enabled" (bool): Whether the test case is enabled

        Example:
            >>> verdicts = test_module.get_all_test_case_verdicts()
            >>> for name, info in verdicts.items():
            ...     print(f"{name}: {info['verdict_name']} (enabled={info['enabled']})")
        """
        result = {}
        test_cases = self.get_all_test_cases()
        for name, tc in test_cases.items():
            result[name] = {
                "verdict": tc.verdict,
                "verdict_name": tc.verdict_name,
                "enabled": tc.enabled
            }
        return result
