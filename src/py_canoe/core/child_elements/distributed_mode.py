

class DistributedMode:
    """
    Provides the distributed mode management API.
    """
    def __init__(self, com_object) -> None:
        self.com_object = com_object

    @property
    def auto_connect_on_program_start(self) -> bool:
        return self.com_object.AutoConnectOnProgramStart

    @auto_connect_on_program_start.setter
    def auto_connect_on_program_start(self, value: bool):
        self.com_object.AutoConnectOnProgramStart = value

    @property
    def auto_disconnect_on_measurement_stop(self) -> bool:
        return self.com_object.AutoDisconnectOnMeasurementStop

    @auto_disconnect_on_measurement_stop.setter
    def auto_disconnect_on_measurement_stop(self, value: bool):
        self.com_object.AutoDisconnectOnMeasurementStop = value

    @property
    def connected(self) -> bool:
        return self.com_object.Connected

    @property
    def remote_time_auto_adjust(self) -> bool:
        return self.com_object.RemoteTimeAutoAdjust

    @remote_time_auto_adjust.setter
    def remote_time_auto_adjust(self, value: bool):
        self.com_object.RemoteTimeAutoAdjust = value

    @property
    def rt_server(self) -> str:
        return self.com_object.RTServer

    @rt_server.setter
    def rt_server(self, value: str):
        self.com_object.RTServer = value

    def connect(self):
        self.com_object.Connect()

    def disconnect(self):
        self.com_object.Disconnect()

    def get_rt_server_occupancy_info(self, remote_address: str) -> 'RTServerOccupancyInfo':
        return RTServerOccupancyInfo(self.com_object.GetRTServerOccupancyInfo(remote_address))


class RTServerOccupancyInfo:
    """
    Represents the occupancy information of a remote test server.
    """
    def __init__(self, com_object) -> None:
        self.com_object = com_object

    @property
    def client(self) -> str:
        return self.com_object.Client

    @property
    def used_in_distributed_mode(self) -> bool:
        return self.com_object.UsedInDistributedMode

    @property
    def used_in_standalone_mode(self) -> bool:
        return self.com_object.UsedInStandaloneMode
