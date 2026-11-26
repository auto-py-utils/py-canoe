from py_canoe.core.child_elements.can_controller import CanController
from py_canoe.core.com_session import dispatch_com_object


class Channel:
    def __init__(self, com_object):
        self.com_object = dispatch_com_object(com_object)

    @property
    def bus_type(self) -> int:
        return self.com_object.BusType

    @property
    def controller(self) -> 'CanController':
        return CanController(self.com_object.Controller)

    @property
    def number(self) -> int:
        return self.com_object.Number
