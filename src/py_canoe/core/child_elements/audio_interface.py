

class AudioInterface:
    def __init__(self, com_object):
        self.com_object = com_object

    def mute(self, line_in_out: int, mute: int | None=None) -> int:
        if mute is None:
            return self.com_object.Mute(line_in_out)
        else:
            self.com_object.Mute(line_in_out)
            return self.com_object.Mute(line_in_out)

    def volume(self, line_in_out: int, volume: int | None=None) -> int:
        if volume is None:
            return self.com_object.Volume(line_in_out)
        else:
            self.com_object.Volume(line_in_out)
            return self.com_object.Volume(line_in_out)

    def connect_to_label(self, line_in_out: int, connection_label: int):
        self.com_object.ConnectToLabel(line_in_out, connection_label)

    def disconnect_from_label(self, line_in_out: int, connection_label: int):
        self.com_object.DisconnectFromLabel(line_in_out, connection_label)
