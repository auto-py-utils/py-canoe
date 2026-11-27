from py_canoe.core.com_session import dispatch_com_object


class DataSourceIssue:
    """
    Represents a single issue from a DataSource import operation.
    """
    def __init__(self, com_object) -> None:
        self.com_object = dispatch_com_object(com_object)

    @property
    def description(self) -> str:
        return self.com_object.Description

    @property
    def emitter(self):
        from py_canoe.core.child_elements.data_source import DataSource
        return DataSource(self.com_object.Emitter)

    @property
    def severity(self) -> int:
        return self.com_object.Severity
