from py_canoe.core.child_elements.buses import Buses
from py_canoe.core.com_session import dispatch_com_object


class SimulationSetup:
    def __init__(self, com_object):
        self.com_object = dispatch_com_object(com_object)

    @property
    def buses(self) -> 'Buses':
        return Buses(self.com_object.Buses)
