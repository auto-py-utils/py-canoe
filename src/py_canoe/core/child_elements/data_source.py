from py_canoe.core.child_elements.data_source_issues import DataSourceIssues
from py_canoe.core.com_session import dispatch_com_object


class DataSource:
    """
    Provides access to the base interface of all data sources.
    """
    def __init__(self, com_object) -> None:
        self.com_object = dispatch_com_object(com_object)

    @property
    def id(self) -> int:
        return self.com_object.Id

    @property
    def import_issues(self) -> 'DataSourceIssues':
        return DataSourceIssues(self.com_object.ImportIssues)

    @property
    def import_parameters_raw(self) -> str:
        return self.com_object.ImportParametersRaw

    @property
    def import_status(self) -> int:
        return self.com_object.ImportStatus

    @property
    def is_group_source(self) -> bool:
        return self.com_object.IsGroupSource

    @property
    def source_format(self) -> int:
        return self.com_object.SourceFormat

    @property
    def source_type(self) -> int:
        return self.com_object.SourceType

    def import_data_source(self, merge_strategy: int) -> int:
        return self.com_object.Import(merge_strategy)
