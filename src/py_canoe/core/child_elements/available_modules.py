from py_canoe.core.child_elements.application_specific_modules import (
    ApplicationSpecificModules,
)
from py_canoe.core.child_elements.basic_modules import BasicModules
from py_canoe.core.com_session import dispatch_com_object


class AvailableModules:
    """
    Represents the collection of known VT module types that can be added to VT System.
    """
    def __init__(self, available_modules_com_obj):
        self.com_object = dispatch_com_object(available_modules_com_obj)

    @property
    def application_specific_modules(self) -> 'ApplicationSpecificModules':
        """Returns the collection of available application specific modules."""
        return ApplicationSpecificModules(self.com_object.ApplicationSpecificModules)

    @property
    def basic_modules(self) -> 'BasicModules':
        """Returns the collection of available basic modules."""
        return BasicModules(self.com_object.BasicModules)
