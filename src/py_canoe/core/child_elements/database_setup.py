from py_canoe.core.child_elements.database import Database
from py_canoe.core.child_elements.databases import Databases


class DatabaseSetup:
    def __init__(self, com_object) -> None:
        self.com_object = com_object

    @property
    def databases(self) -> 'Databases':
        return Databases(self.com_object.Databases)

