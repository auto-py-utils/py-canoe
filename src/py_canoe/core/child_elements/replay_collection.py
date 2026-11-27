from py_canoe.core.com_session import (
    ComObjectProxy,
    dispatch_com_object,
    invoke_com_dispatch,
)


class ReplayCollection:
    """The ReplayCollection object represents the Replay Blocks of the CANoe application."""
    def __init__(self, replay_collection_com_obj):
        self.com_object = replay_collection_com_obj

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int) -> 'ReplayBlock':
        return ReplayBlock(self.com_object.Item(index))

    def add(self, name: str) -> 'ReplayBlock':
        return ReplayBlock(self.com_object.Add(name))

    def remove(self, index: int):
        self.com_object.Remove(index)


class ReplayBlock:
    """The ReplayBlock object represents a Replay Block of the CANoe application."""
    def __init__(self, replay_block_com_obj):
        self.com_object = dispatch_com_object(replay_block_com_obj)

    @property
    def enabled(self) -> bool:
        return self.com_object.Enabled

    @enabled.setter
    def enabled(self, value: bool):
        self.com_object.Enabled = value

    @property
    def name(self) -> str:
        if isinstance(self.com_object, ComObjectProxy):
            return invoke_com_dispatch(
                self.com_object, 3, "property_get", (8, 0), ()
            )
        return self.com_object.Name

    @name.setter
    def name(self, value: str):
        self.com_object.Name = value

    @property
    def path(self) -> str:
        if isinstance(self.com_object, ComObjectProxy):
            return invoke_com_dispatch(
                self.com_object, 4, "property_get", (8, 0), ()
            )
        return self.com_object.Path

    @path.setter
    def path(self, value: str):
        if isinstance(self.com_object, ComObjectProxy):
            invoke_com_dispatch(
                self.com_object, 4, "property_put", (24, 0), ((8, 1),), value
            )
            return
        self.com_object.Path = value

    def start(self):
        if isinstance(self.com_object, ComObjectProxy):
            invoke_com_dispatch(self.com_object, 5, "method", (24, 0), ())
            return
        self.com_object.Start()

    def stop(self):
        if isinstance(self.com_object, ComObjectProxy):
            invoke_com_dispatch(self.com_object, 6, "method", (24, 0), ())
            return
        self.com_object.Stop()
