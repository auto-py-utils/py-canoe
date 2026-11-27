from py_canoe.core.child_elements.c_library import CLibrary
from py_canoe.core.com_session import dispatch_com_object


class CLibraries:
    """
    Represents the collection of C libraries in a CANoe configuration.
    """
    def __init__(self, com_object) -> None:
        self.com_object = dispatch_com_object(com_object)

    @property
    def count(self) -> int:
        """Returns the number of CLibrary objects in the collection."""
        return self.com_object.Count

    def item(self, index: int) -> 'CLibrary':
        """Returns the CLibrary object at the specified index (1-based)."""
        return CLibrary(self.com_object.Item(index))

    def add(self, file_path: str) -> 'CLibrary':
        """Adds a new C library to the collection and returns the CLibrary object."""
        return CLibrary(self.com_object.Add(file_path))

    def remove(self, clibrary: 'CLibrary'):
        """Removes the specified CLibrary object from the collection."""
        self.com_object.Remove(clibrary.com_object)
