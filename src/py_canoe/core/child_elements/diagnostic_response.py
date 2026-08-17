from typing import Union


class DiagnosticResponse:
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def positive(self) -> bool:
        return self.com_object.Positive

    @property
    def response_code(self) -> int:
        return self.com_object.ResponseCode

    @property
    def is_response_pending(self) -> bool:
        return not self.positive and self.response_code == 0x78

    @property
    def sender(self) -> str:
        return self.com_object.Sender

    @property
    def stream(self) -> bytearray:
        return bytearray(self.com_object.Stream)

    def get_complex_iteration_count(self, qualifier: str) -> int:
        return self.com_object.GetComplexIterationCount(qualifier)

    def get_complex_parameter(self, qualifier: str, iteration: int, sub_parameter: str, mode: int) -> Union[bytearray, int, str]:
        return self.com_object.GetComplexParameter(qualifier, iteration, sub_parameter, mode)

    def get_parameter(self, qualifier: str, mode: int) -> Union[bytearray, int, str]:
        return self.com_object.GetParameter(qualifier, mode)

    def is_complex_parameter(self, qualifier: str) -> bool:
        return self.com_object.IsComplexParameter(qualifier)
