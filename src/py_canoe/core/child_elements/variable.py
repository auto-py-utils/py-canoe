from typing import Union
import win32com.client

from py_canoe.helpers.common import logger, DoEventsUntil
from py_canoe.core.child_elements.encodings import Encodings
from py_canoe.core.child_elements.variable_events import VariableEvents


class Variable:
    def __init__(self, com_object, enable_events: bool = True):
        self.com_object = win32com.client.Dispatch(com_object)
        self.enable_events = enable_events
        if self.enable_events:
            self.variable_events: VariableEvents = win32com.client.WithEvents(self.com_object, VariableEvents)

    @property
    def analysis_only(self) -> bool:
        return self.com_object.AnalysisOnly

    @analysis_only.setter
    def analysis_only(self, value: bool = False):
        self.com_object.AnalysisOnly = value

    @property
    def bit_count(self) -> int:
        return self.com_object.BitCount

    @property
    def comment(self) -> str:
        return self.com_object.Comment

    @property
    def element_count(self) -> int:
        return self.com_object.ElementCount

    @property
    def encodings(self) -> Encodings:
        return Encodings(self.com_object.Encodings)

    @property
    def full_name(self) -> str:
        return self.com_object.FullName

    @property
    def init_value(self) -> Union[int, float]:
        return self.com_object.InitValue

    @property
    def is_array(self) -> bool:
        return self.com_object.IsArray

    @property
    def is_member(self) -> bool:
        return self.com_object.IsMember

    @property
    def is_signed(self) -> bool:
        return self.com_object.IsSigned

    @property
    def is_struct(self) -> bool:
        return self.com_object.IsStruct

    @property
    def max_value(self) -> Union[int, float]:
        return self.com_object.MaxValue

    @property
    def member_name(self) -> str:
        return self.com_object.MemberName

    @property
    def members(self):
        from py_canoe.core.child_elements.variables import Variables
        return Variables(self.com_object.Members)

    @property
    def min_value(self) -> Union[int, float]:
        return self.com_object.MinValue

    @property
    def name(self) -> str:
        return self.com_object.Name

    @property
    def notification_type(self) -> int:
        return self.com_object.NotificationType

    @property
    def physical_init_value(self) -> Union[int, float]:
        return self.com_object.PhysicalInitValue

    @property
    def physical_value(self) -> Union[int, float]:
        return self.com_object.PhysicalValue

    @property
    def read_only(self) -> bool:
        return self.com_object.ReadOnly

    @property
    def type(self) -> int:
        return self.com_object.Type

    @property
    def unit(self) -> str:
        return self.com_object.Unit

    def get_value(self):
        return self.com_object.Value

    def set_value(self, value, timeout: Union[int, float]):
        status: bool = False
        self.com_object.Value = value
        if hasattr(self, 'variable_events') and self.variable_events:
            self.variable_events.VARIABLE_UPDATED = False
            status = DoEventsUntil(lambda: self.variable_events.VARIABLE_UPDATED, timeout, "Variable Update")
            if status:
                logger.info(f"Variable '{self.full_name}' updated successfully to: {value}")
        return status

    def begin_struct_update(self):
        self.com_object.BeginStructUpdate()

    def end_struct_update(self):
        self.com_object.EndStructUpdate()

    def get_member_phys_value(self, member_name: str) -> Union[int, float]:
        return self.com_object.GetMemberPhysValue(member_name)

    def get_member_value(self, member_name: str) -> Union[int, float]:
        return self.com_object.GetMemberValue(member_name)

    def get_symbolic_value_name(self, value: Union[int, float]) -> str:
        return self.com_object.GetSymbolicValueName(value)

    def set_member_phys_value(self, member_name: str, value: Union[int, float]):
        self.com_object.SetMemberPhysValue(member_name, value)

    def set_member_value(self, member_name: str, value: Union[int, float]):
        self.com_object.SetMemberValue(member_name, value)

    def set_symbolic_value_name(self, value: Union[int, float], name: str):
        self.com_object.SetSymbolicValueName(value, name)
