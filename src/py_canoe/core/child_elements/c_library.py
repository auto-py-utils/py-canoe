from py_canoe.core.com_session import dispatch_com_object


class CLibrary:
    """
    Represents a single C library in a CANoe configuration.
    """
    def __init__(self, com_object) -> None:
        self.com_object = dispatch_com_object(com_object)

    @property
    def enabled(self) -> bool:
        """Get or set whether the library is enabled."""
        return self.com_object.Enabled

    @enabled.setter
    def enabled(self, value: bool):
        self.com_object.Enabled = value

    @property
    def full_name(self) -> str:
        """Returns the complete path to the C library file."""
        return self.com_object.FullName

    @property
    def name(self) -> str:
        """Returns the name of the C library file."""
        return self.com_object.Name

    @property
    def path(self) -> str:
        """Returns the path to the C library file."""
        return self.com_object.Path
