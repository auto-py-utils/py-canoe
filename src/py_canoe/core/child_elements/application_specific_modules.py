from py_canoe.core.child_elements.application_specific_module import (
    ApplicationSpecificModule,
)
from py_canoe.core.com_session import dispatch_com_object


class ApplicationSpecificModules:
    """Represents the collection of available application specific modules."""
    def __init__(self, app_specific_modules_com_obj):
        self.com_object = dispatch_com_object(app_specific_modules_com_obj)

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int) -> 'ApplicationSpecificModule':
        return ApplicationSpecificModule(self.com_object.Item(index))
