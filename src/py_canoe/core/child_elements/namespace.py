from py_canoe.core.child_elements.variables import Variables


class Namespace:
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def comment(self):
        return self.com_object.Comment

    @property
    def name(self):
        return self.com_object.Name

    def variables(self) -> 'Variables':
        return Variables(self.com_object.Variables, namespace_name=self.name)

    def namespaces(self):
        from py_canoe.core.child_elements.namespaces import Namespaces
        return Namespaces(self.com_object.Namespaces)
