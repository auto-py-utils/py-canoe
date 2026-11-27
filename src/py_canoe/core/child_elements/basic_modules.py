from py_canoe.core.child_elements.basic_module import BasicModule
from py_canoe.core.com_session import dispatch_com_object


class BasicModules:
    """Represents the collection of available basic modules."""
    def __init__(self, basic_modules_com_obj):
        self.com_object = dispatch_com_object(basic_modules_com_obj)

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int) -> 'BasicModule':
        return BasicModule(self.com_object.Item(index))
