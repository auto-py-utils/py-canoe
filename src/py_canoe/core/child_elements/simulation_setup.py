import win32com.client

from py_canoe.core.child_elements.buses import Buses


class SimulationSetup:
    def __init__(self, com_object):
        self.com_object = win32com.client.Dispatch(com_object)

    @property
    def buses(self) -> 'Buses':
        return Buses(self.com_object.Buses)
