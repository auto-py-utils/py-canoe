from py_canoe.core.com_session import dispatch_com_object


class VisualSequenceSetup:
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def visual_sequences(self) -> 'VisualSequences':
        return VisualSequences(self.com_object.VisualSequences)


class VisualSequences:
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int) -> 'VisualSequence':
        return VisualSequence(self.com_object.Item(index))

    def import_visual_sequence(self, name: str, file_name: str):
        return self.com_object.Import(name, file_name)

    def remove(self, index: int):
        self.com_object.Remove(index)


class VisualSequence:
    def __init__(self, com_object):
        self.com_object = dispatch_com_object(com_object)

    @property
    def name(self) -> str:
        return self.com_object.Name

    def is_running(self) -> bool:
        return self.com_object.IsRunning()

    def start(self):
        self.com_object.Start()

    def stop(self):
        self.com_object.Stop()
