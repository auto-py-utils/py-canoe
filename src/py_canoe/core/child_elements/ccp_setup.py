
from py_canoe.core.child_elements.mc_ecus import McECUs


class CCPSetup:
    """
    The CCPSetup object represents the CCP settings of a CANoe configuration.
    """
    def __init__(self, com_object) -> None:
        self.com_object = com_object

    @property
    def ecus(self) -> 'McECUs':
        return McECUs(self.com_object.ECUs)
