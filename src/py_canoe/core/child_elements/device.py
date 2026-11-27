from py_canoe.core.child_elements.application_socket import ApplicationSocket
from py_canoe.core.child_elements.audio_interface import AudioInterface
from py_canoe.core.child_elements.diagnostic import Diagnostic
from py_canoe.core.child_elements.most_disassembler import MostDisassembler
from py_canoe.core.child_elements.most_network_interface import MostNetworkInterface


class Device:
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def application_socket(self) -> ApplicationSocket:
        return ApplicationSocket(self.com_object.ApplicationSocket)

    @property
    def audio_interface(self) -> AudioInterface:
        return AudioInterface(self.com_object.AudioInterface)

    @property
    def diagnostic(self) -> Diagnostic:
        return Diagnostic(self.com_object.Diagnostic)

    @property
    def disassembler(self) -> MostDisassembler:
        return MostDisassembler(self.com_object.Disassembler)

    @property
    def name(self) -> str:
        return self.com_object.Name

    @property
    def network_interface(self) -> MostNetworkInterface:
        return MostNetworkInterface(self.com_object.NetworkInterface)
