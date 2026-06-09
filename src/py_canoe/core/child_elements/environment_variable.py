from typing import Union

from py_canoe.helpers.common import DoEventsUntil

ENV_VAR_CHANGE_TIMEOUT = 1


class EnvironmentVariable:
    def __init__(self, com_object):
        self.com_object = com_object
        self.VALUE_TABLE_NOTIFICATION_TYPE = {
            0: "cValue",
            1: "cValueAndTime",
            2: "cValueAndTimeU"
        }
        self.VALUE_TABLE_TYPE = {
            0: "INTEGER",
            1: "FLOAT",
            2: "STRING",
            3: "DATA"
        }

    @property
    def handle(self) -> int:
        return self.com_object.Handle

    @handle.setter
    def handle(self, value: int):
        self.com_object.Handle = value

    @property
    def notification_type(self) -> int:
        return self.com_object.NotificationType

    @notification_type.setter
    def notification_type(self, value: int):
        self.com_object.NotificationType = value

    @property
    def type(self) -> int:
        return self.com_object.Type

    @property
    def value(self) -> Union[str, int, float]:
        return self.com_object.Value

    @value.setter
    def value(self, value: Union[str, int, float]):
        self.com_object.Value = value
        DoEventsUntil(lambda: self._check_value_updated(value), ENV_VAR_CHANGE_TIMEOUT, "Environment Variable Change")

    def _check_value_updated(self, value) -> bool:
        set_value = value
        get_value = self.value if self.type != 3 else tuple(self.value)
        return get_value == set_value
