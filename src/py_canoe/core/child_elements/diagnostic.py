from win32com.universal import com_error

from py_canoe.core.child_elements.diagnostic_request import DiagnosticRequest
from py_canoe.helpers.common import logger

class Diagnostic:
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def tester_present_status(self) -> bool:
        return self.com_object.TesterPresentStatus

    def create_request(self, primitive_path, **kwargs) -> DiagnosticRequest:
        request = self.com_object.CreateRequest(primitive_path)
        for key, value in kwargs.items():
            try:
                request.SetParameter(key, value)
            except com_error:
                logger.error("Failed to create parametrized diagnostic request due to %s attribute.", key)
                raise
        return DiagnosticRequest(request)

    def create_request_from_stream(self, byte_stream: bytearray) -> DiagnosticRequest:
        return DiagnosticRequest(self.com_object.CreateRequestFromStream(byte_stream))

    def diag_start_tester_present(self):
        self.com_object.DiagStartTesterPresent()

    def diag_stop_tester_present(self):
        self.com_object.DiagStopTesterPresent()
