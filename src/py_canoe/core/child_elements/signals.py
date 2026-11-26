

class Signals:
    def __init__(self, signals_com_object):
        self.com_object = signals_com_object


class Signal:
    def __init__(self, signal_com_object):
        self.com_object = signal_com_object

    @property
    def full_name(self) -> str:
        return self.com_object.FullName

    @property
    def is_online(self) -> bool:
        return self.com_object.IsOnline

    @property
    def raw_value(self) -> int:
        return self.com_object.RawValue

    @raw_value.setter
    def raw_value(self, value: int):
        self.com_object.RawValue = value

    @property
    def state(self) -> int:
        return self.com_object.State

    @property
    def value(self) -> int | float:
        return self.com_object.Value

    @value.setter
    def value(self, value: float):
        self.com_object.Value = value
