from py_canoe.core.com_session import dispatch_com_object


class DataSourceFile:
    """
    Represents a single file in a DataSourceFiles collection.
    """
    def __init__(self, com_object) -> None:
        self.com_object = dispatch_com_object(com_object)

    @property
    def full_name(self) -> str:
        return self.com_object.FullName

    @property
    def name(self) -> str:
        return self.com_object.Name

    @property
    def path(self) -> str:
        return self.com_object.Path
