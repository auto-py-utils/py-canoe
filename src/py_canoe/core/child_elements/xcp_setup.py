
from py_canoe.core.child_elements.mc_ecus import McECUs


class XCPSetup:
    def __init__(self, com_object) -> None:
        self.com_object = com_object

    @property
    def mcus(self) -> 'McECUs':
        return McECUs(self.com_object.MCUs)
