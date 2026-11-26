from py_canoe.core.com_session import dispatch_com_object


class Participant:
    """
    Represents a single participant associated with an ApplicationModel.
    """
    def __init__(self, com_object) -> None:
        self.com_object = dispatch_com_object(com_object)

    @property
    def name(self) -> str:
        return self.com_object.Name

    @property
    def path(self) -> str:
        return self.com_object.Path
