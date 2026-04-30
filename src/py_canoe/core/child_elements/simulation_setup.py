class SimulationSetup:
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def buses(self) -> 'SimulationBuses':
        return SimulationBuses(self.com_object.Buses)


class SimulationBuses:
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int) -> 'SimulationBus':
        return SimulationBus(self.com_object.Item(index))


class SimulationBus:
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def name(self) -> str:
        return self.com_object.Name

    @property
    def databases(self) -> 'SimulationBusDatabases':
        return SimulationBusDatabases(self.com_object.Databases)


class SimulationBusDatabases:
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int) -> 'SimulationBusDatabase':
        return SimulationBusDatabase(self.com_object.Item(index))


class SimulationBusDatabase:
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def full_name(self) -> str:
        return self.com_object.FullName

    @property
    def name(self) -> str:
        return self.com_object.Name
