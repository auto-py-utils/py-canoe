from py_canoe.core.child_elements.test_environments import TestEnvironments
from py_canoe.core.com_session import dispatch_com_object


class TestSetup:
    """The TestSetup object represents CANoe's test setup."""
    def __init__(self, com_object):
        self.com_object = dispatch_com_object(com_object)

    def save_all(self, prompt_user=False) -> None:
        self.com_object.SaveAll(prompt_user)

    @property
    def test_environments(self) -> 'TestEnvironments':
        return TestEnvironments(self.com_object.TestEnvironments)
