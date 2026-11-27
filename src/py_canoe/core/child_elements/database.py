from py_canoe.core.com_session import dispatch_com_object


class Database:
    """The Database object represents the assigned database of the CANoe application."""
    def __init__(self, com_object):
        self.com_object = dispatch_com_object(com_object)

    @property
    def channel(self) -> int:
        return self.com_object.Channel

    @channel.setter
    def channel(self, channel: int) -> None:
        self.com_object.Channel = channel

    @property
    def full_name(self) -> str:
        return self.com_object.FullName

    @full_name.setter
    def full_name(self, full_name: str) -> None:
        self.com_object.FullName = full_name

    @property
    def name(self) -> str:
        return self.com_object.Name

    @property
    def path(self) -> str:
        return self.com_object.Path
