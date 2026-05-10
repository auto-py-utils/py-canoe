import win32com.client


class Database:
    def __init__(self, com_object):
        self.com_object = win32com.client.Dispatch(com_object)

    @property
    def full_name(self) -> str:
        return self.com_object.FullName

    @property
    def name(self) -> str:
        return self.com_object.Name
