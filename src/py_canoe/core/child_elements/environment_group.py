from py_canoe.core.child_elements.environment_array import EnvironmentArray


class EnvironmentGroup:
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def array(self) -> 'EnvironmentArray':
        return EnvironmentArray(self.com_object.Array)

    def add(self, variable):
        self.com_object.Add(variable)

    def get_values(self):
        return self.com_object.GetValues()

    def remove(self, variable):
        self.com_object.Remove(variable)

    def set_values(self, values: list):
        self.com_object.SetValues(values)
