from py_canoe.core.com_session import dispatch_com_object


class NetworkAdapters:
    """Represents the collection of available network adapters for VT System communication."""
    def __init__(self, network_adapters_com_obj):
        self.com_object = dispatch_com_object(network_adapters_com_obj)

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int):
        return self.com_object.Item(index)  # Returns a NetworkAdapter object
