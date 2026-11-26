from py_canoe.core.com_session import dispatch_com_object


class PanelSetup:
    """
    The PanelSetup object represents the panel settings of a CANoe configuration.
    """
    def __init__(self, com_object) -> None:
        self.com_object = com_object

    def panels(self, type: int) -> 'Panels':
        return Panels(self.com_object.Panels(type))

    def save_positions(self):
        self.com_object.SavePositions()


class Panels:
    def __init__(self, com_object) -> None:
        self.com_object = com_object

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int) -> 'Panel':
        return Panel(self.com_object.Item(index))

    def add(self, type: int) -> 'Panel':
        return Panel(self.com_object.Add(type))

    def remove(self, index: int):
        self.com_object.Remove(index)


class Panel:
    def __init__(self, com_object) -> None:
        self.com_object = dispatch_com_object(com_object)

    @property
    def full_name(self) -> str:
        return self.com_object.FullName

    @full_name.setter
    def full_name(self, full_name: str):
        self.com_object.FullName = full_name

    @property
    def height(self) -> int:
        return self.com_object.Height

    @property
    def left(self) -> int:
        return self.com_object.Left

    @left.setter
    def left(self, value: int):
        self.com_object.Left = value

    @property
    def name(self) -> str:
        return self.com_object.Name

    @property
    def orphaned(self) -> bool:
        return self.com_object.Orphaned
    @property
    def path(self) -> str:
        return self.com_object.Path

    @property
    def top(self) -> int:
        return self.com_object.Top

    @top.setter
    def top(self, value: int):
        self.com_object.Top = value

    @property
    def visible(self) -> bool:
        return self.com_object.Visible

    @visible.setter
    def visible(self, value: bool):
        self.com_object.Visible = value

    @property
    def width(self) -> int:
        return self.com_object.Width

    @property
    def window_type(self) -> int:
        return self.com_object.WindowType

    @window_type.setter
    def window_type(self, value: int):
        self.com_object.WindowType = value
