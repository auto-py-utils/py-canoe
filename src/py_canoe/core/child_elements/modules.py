import win32com.client


class Modules:
    """The Modules object represents the modules of a test module in CANoe's test setup or a node in CANoe's Simulation Setup / System and Communication Setup."""
    def __init__(self, modules_com_obj):
        self.com_object = modules_com_obj

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int) -> 'Module':
        return Module(self.com_object.Item(index))

    def add(self, full_name: str) -> 'Module':
        return Module(self.com_object.Add(full_name))

    def remove(self, index: int):
        self.com_object.Remove(index)


class Module:
    """The Module object represents the modules within a test module in CANoe's test setup or a node of the Simulation Setup / System and Communication Setup of the CANoe application."""
    def __init__(self, module_com_obj):
        self.com_object = win32com.client.Dispatch(module_com_obj)

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

    @property
    def references(self) -> 'References':
        return References(self.com_object.References)


class References:
    """The References object represents assemblies that are used by a .NET test library."""
    def __init__(self, references_com_obj):
        self.com_object = references_com_obj

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int) -> 'Reference':
        return Reference(self.com_object.Item(index))

    def add(self, full_name: str) -> 'Reference':
        return Reference(self.com_object.Add(full_name))

    def remove(self, index: int):
        self.com_object.Remove(index)


class Reference:
    """The Reference object represents a component that is used by a .NET test library module."""
    def __init__(self, reference_com_obj):
        self.com_object = win32com.client.Dispatch(reference_com_obj)

    @property
    def full_name(self) -> str:
        return self.com_object.FullName

    @property
    def name(self) -> str:
        return self.com_object.Name

    @property
    def path(self) -> str:
        return self.com_object.Path