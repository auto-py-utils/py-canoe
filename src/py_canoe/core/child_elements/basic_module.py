from py_canoe.core.com_session import dispatch_com_object


class BasicModule:
    """
    Represents a basic VT System module (e.g., VT1004, VT2004, etc.).
    """
    def __init__(self, basic_module_com_obj):
        self.com_object = dispatch_com_object(basic_module_com_obj)

    @property
    def name(self) -> str:
        """The name of the module."""
        return self.com_object.Name

    @property
    def type(self) -> int:
        """The type of the module (e.g. 1004)."""
        return self.com_object.Type
