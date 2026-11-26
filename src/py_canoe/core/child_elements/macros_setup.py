from py_canoe.core.com_session import dispatch_com_object


class MacrosSetup:
    """
    The MacrosSetup object represents the macros settings of a CANoe configuration.
    """
    def __init__(self, com_object) -> None:
        self.com_object = com_object

    @property
    def macros(self) -> 'Macros':
        return Macros(self.com_object.Macros)

    def play(self, macro_file: str):
        self.com_object.Play(macro_file)


class Macros:
    def __init__(self, com_object) -> None:
        self.com_object = com_object

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int) -> 'Macro':
        return Macro(self.com_object.Item(index))

    def add_ex(self, file_name: str, full_name: str) -> 'Macro':
        return Macro(self.com_object.AddEx(file_name, full_name))


class Macro:
    def __init__(self, com_object) -> None:
        self.com_object = dispatch_com_object(com_object)

    @property
    def name(self) -> str:
        return self.com_object.Name

    @property
    def path(self) -> str:
        return self.com_object.Path

    def is_running(self) -> bool:
        return self.com_object.IsRunning()

    def start(self):
        self.com_object.Start()

    def stop(self):
        self.com_object.Stop()
