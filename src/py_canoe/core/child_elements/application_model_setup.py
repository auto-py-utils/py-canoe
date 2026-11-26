
from py_canoe.core.child_elements.application_models import ApplicationModels


class ApplicationModelSetup:
    """
    Provides access to the application model management API.
    """
    def __init__(self, com_object) -> None:
        self.com_object = com_object

    @property
    def application_models(self) -> 'ApplicationModels':
        return ApplicationModels(self.com_object.ApplicationModels)
