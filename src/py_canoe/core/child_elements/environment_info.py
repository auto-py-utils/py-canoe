class EnvironmentInfo:
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def read(self) -> bool:
        return self.com_object.Read

    @property
    def write(self) -> bool:
        return self.com_object.Write

    def get_info(self) -> list:
        return self.com_object.GetInfo()
