import win32com.client


class TestLibrary:
    """The TestLibrary object represents a test case file within an XML or .NET test module.

    Properties:
        full_name: Returns the complete path to the test case file (read-only).
        name: Returns the filename of the test case file without path and
              filename extension (read-only).
        path: Returns the complete path to the test case file (read-only).
    """

    __test__ = False

    def __init__(self, com_object):
        self.com_object = win32com.client.Dispatch(com_object)

    def __getattr__(self, item):
        return getattr(self.com_object, item)

    @property
    def full_name(self) -> str:
        """Returns the complete path to the test case file."""
        return self.com_object.FullName

    @property
    def name(self) -> str:
        """Returns the filename of the test case file without path and filename extension."""
        return self.com_object.Name

    @property
    def path(self) -> str:
        """Returns the complete path to the test case file."""
        return self.com_object.Path
