import win32com.client

from py_canoe.helpers.common import logger


class TestCase:
    """The TestCase object represents a test case within a test module's test sequence.

    Note: The TestCase data (e.g. Verdict) does not auto-update. Call refresh() or
    use TestModule.get_all_test_cases() to get the latest state from CANoe.
    """

    __test__ = False

    VALUE_TABLE_VERDICT = {
        0: "NotAvailable",
        1: "Passed",
        2: "Failed",
        3: "None",
        4: "Inconclusive",
        5: "ErrorInTestSystem"
    }

    def __init__(self, com_object):
        self.obj = com_object
        self.com_object = win32com.client.Dispatch(com_object)

    @property
    def name(self) -> str:
        """Returns the name of the test case."""
        return self.com_object.Name

    @property
    def title(self) -> str:
        """Returns the title of the test case. Introduced in CANoe v17.

        Some test modules (e.g. CAPL test modules, or CANoe versions / module
        types that do not expose a title) raise AttributeError when accessing
        Title. In that case we return an empty string so callers can fall back
        to matching by name.
        """
        try:
            return self.com_object.Title
        except AttributeError:
            return ""

    @property
    def ident(self) -> str:
        """Returns the ID of the test case. Only implemented in XML test modules."""
        return self.com_object.Ident

    @property
    def enabled(self) -> bool:
        """Returns whether the test case is enabled (checked)."""
        return self.com_object.Enabled

    @enabled.setter
    def enabled(self, value: bool):
        """Enable or disable the test case."""
        self.com_object.Enabled = value

    @property
    def verdict(self) -> int:
        """Returns the verdict of the test case.

        Returns:
            int: 0=NotAvailable, 1=Passed, 2=Failed, 3=None, 4=Inconclusive, 5=ErrorInTestSystem
        """
        return self.com_object.Verdict

    @property
    def verdict_name(self) -> str:
        """Returns the verdict as a human-readable string."""
        return self.VALUE_TABLE_VERDICT.get(self.com_object.Verdict, "Unknown")

    def refresh(self):
        """Re-dispatch the COM object to get fresh data from CANoe.

        The TestCase COM object data does not auto-update. Call this method
        to refresh the state (e.g. Verdict) after test execution.
        """
        try:
            self.com_object = win32com.client.Dispatch(self.obj)
            logger.info(f'Refreshed test case ({self.name}) data.')
        except Exception as e:
            logger.error(f'Error refreshing test case: {e}')

    def to_dict(self) -> dict:
        """Returns a dictionary representation of the test case."""
        return {
            "name": self.name,
            "title": self.title,
            "enabled": self.enabled,
            "verdict": self.verdict,
            "verdict_name": self.verdict_name
        }

    def __repr__(self) -> str:
        return str(self.to_dict())
