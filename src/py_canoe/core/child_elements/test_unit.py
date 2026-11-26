from py_canoe.core.com_session import dispatch_com_object


class TestUnit:
    """The TestUnit object represents a single test unit within a test configuration."""

    def __init__(self, com_object):
        self.com_object = dispatch_com_object(com_object)

    def __getattr__(self, item):
        return getattr(self.com_object, item)

    @property
    def caption(self) -> str:
        return self.com_object.Caption

    @property
    def elements(self):
        from py_canoe.core.child_elements.test_tree_elements import TestTreeElements

        return TestTreeElements(self.com_object.Elements)

    @property
    def enabled(self) -> bool:
        return self.com_object.Enabled

    @enabled.setter
    def enabled(self, value: bool):
        self.com_object.Enabled = value

    @property
    def id(self) -> str:
        return self.com_object.Id

    @property
    def full_path(self) -> str:
        return self.com_object.FullPath

    @property
    def name(self) -> str:
        return self.com_object.Name

    @property
    def report(self):
        from py_canoe.core.child_elements.test_unit_report import TestUnitReport

        return TestUnitReport(self.com_object.Report)

    @property
    def type(self) -> int:
        return self.com_object.Type

    @property
    def verdict(self) -> int:
        return self.com_object.Verdict

    def contains_id(self, test_case_id: int) -> bool:
        return self.com_object.ContainsId(test_case_id)

    def get_variant(self, name: str):
        return self.com_object.GetVariant(name)

    def set_variant(self, name: str, value):
        self.com_object.SetVariant(name, value)

    def variant_convert_to_description(self, name: str, value):
        return self.com_object.VariantConvertToDescription(name, value)

    def variant_convert_to_numeric_value(self, name: str, description: str):
        return self.com_object.VariantConvertToNumericValue(name, description)

