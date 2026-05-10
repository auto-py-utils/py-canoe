import win32com.client

from py_canoe.core.child_elements.databases import Databases


class Bus:
    def __init__(self, com_object):
        self.com_object = win32com.client.Dispatch(com_object)

    @property
    def name(self) -> str:
        return self.com_object.Name

    @property
    def databases(self) -> 'Databases':
        return Databases(self.com_object.Databases)
