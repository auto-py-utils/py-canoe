from py_canoe.core.com_session import dispatch_com_object


class FDXFiles:
    """
    The FDXFiles object represents the collection of FDX files in a CANoe configuration.
    """
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int) -> 'FDXFile':
        return FDXFile(self.com_object.Item(index))

    def add(self, file: str) -> 'FDXFile':
        return FDXFile(self.com_object.Add(file))

    def remove(self, index: int):
        self.com_object.Remove(index)


class FDXFile:
    """
    The FDXFile object represents a single FDX file in a CANoe configuration.
    """
    def __init__(self, com_object):
        self.com_object = dispatch_com_object(com_object)

    @property
    def enabled(self) -> bool:
        return self.com_object.Enabled

    @enabled.setter
    def enabled(self, value: bool):
        self.com_object.Enabled = value

    @property
    def full_name(self) -> str:
        return self.com_object.FullName

    @property
    def name(self) -> str:
        return self.com_object.Name

    @property
    def path(self) -> str:
        return self.com_object.Path
