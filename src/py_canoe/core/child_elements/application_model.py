from py_canoe.core.child_elements.application_model_files import ApplicationModelFiles
from py_canoe.core.child_elements.participants import Participants
from py_canoe.core.com_session import dispatch_com_object


class ApplicationModel:
    """
    Represents a single application model.
    """
    def __init__(self, com_object) -> None:
        self.com_object = dispatch_com_object(com_object)

    @property
    def application_model_files(self) -> 'ApplicationModelFiles':
        return ApplicationModelFiles(self.com_object.ApplicationModelFiles)

    @property
    def is_active(self) -> bool:
        return self.com_object.IsActive

    @property
    def participants(self) -> 'Participants':
        return Participants(self.com_object.Participants)
