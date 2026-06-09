import win32com.client


class McECUs:
    """
    The McECUs object represents the collection of all configured CCP/XCP ECUs.
    """
    def __init__(self, com_object) -> None:
        self.com_object = com_object

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int) -> 'McECU':
        return McECU(self.com_object.Item(index))

    def add(self, db_path: str, transport_layer: int) -> 'McECU':
        return McECU(self.com_object.Add(db_path, transport_layer))

    def add_configuration(self, cfg_path: str):
        return self.com_object.AddConfiguration(cfg_path)

    def remove(self, index: int):
        self.com_object.Remove(index)


class McECU:
    """
    The McECU object represents a CCP / an XCP ECU.
    """
    def __init__(self, com_object) -> None:
        self.com_object = win32com.client.Dispatch(com_object)

    @property
    def active(self) -> bool:
        return self.com_object.Active

    @active.setter
    def active(self, value: bool):
        self.com_object.Active = value

    @property
    def bus_type(self) -> int:
        return self.com_object.BusType

    @bus_type.setter
    def bus_type(self, value: int):
        self.com_object.BusType = value

    @property
    def can_settings(self) -> 'McCANSettings':
        return McCANSettings(self.com_object.CANSettings)

    @property
    def check_eprom_identifier(self) -> bool:
        return self.com_object.CheckEPROMIdentifier

    @property
    def connect_mode(self) -> int:
        return self.com_object.ConnectMode

    @connect_mode.setter
    def connect_mode(self, value: int):
        self.com_object.ConnectMode = value

    @property
    def connect_on_measurement_start(self) -> bool:
        return self.com_object.ConnectOnMeasurementStart

    @connect_on_measurement_start.setter
    def connect_on_measurement_start(self, value: bool):
        self.com_object.ConnectOnMeasurementStart = value

    @property
    def daq_timeout(self) -> int:
        return self.com_object.DAQTimeout

    @daq_timeout.setter
    def daq_timeout(self, value: int):
        self.com_object.DAQTimeout = value

    @property
    def disable_variable_updates(self) -> bool:
        return self.com_object.DisableVariableUpdates

    @disable_variable_updates.setter
    def disable_variable_updates(self, value: bool):
        self.com_object.DisableVariableUpdates = value

    @property
    def disconnect_on_measurement_stop(self) -> bool:
        return self.com_object.DisconnectOnMeasurementStop

    @disconnect_on_measurement_stop.setter
    def disconnect_on_measurement_stop(self, value: bool):
        self.com_object.DisconnectOnMeasurementStop = value

    @property
    def ethernet_settings(self) -> 'McEthernetSettings':
        return McEthernetSettings(self.com_object.EthernetSettings)

    @property
    def flexray_settings(self) -> 'McFlexRaySettings':
        return McFlexRaySettings(self.com_object.FlexRaySettings)

    @property
    def master_id(self) -> int:
        return self.com_object.MasterID

    @master_id.setter
    def master_id(self, value: int):
        self.com_object.MasterID = value

    @property
    def measurement_groups(self) -> str:
        return self.com_object.MeasurementGroups

    @property
    def name(self) -> str:
        return self.com_object.Name

    @property
    def number_of_connection_attempts(self) -> int:
        return self.com_object.NumberOfConnectionAttempts

    @property
    def observer_active(self) -> bool:
        return self.com_object.ObserverActive

    @property
    def page_switching_active(self) -> bool:
        return self.com_object.PageSwitchingActive

    @property
    def protocol(self) -> int:
        return self.com_object.Protocol

    @property
    def ram_page(self) -> int:
        return self.com_object.RAMPage

    @property
    def reconnect_allowed_after_error(self) -> bool:
        return self.com_object.ReconnectAllowedAfterError

    @reconnect_allowed_after_error.setter
    def reconnect_allowed_after_error(self, value: bool):
        self.com_object.ReconnectAllowedAfterError = value

    @property
    def reset_variables_after_disconnect(self) -> bool:
        return self.com_object.ResetVariablesAfterDisconnect

    @reset_variables_after_disconnect.setter
    def reset_variables_after_disconnect(self, value: bool):
        self.com_object.ResetVariablesAfterDisconnect = value

    @property
    def response_timeout(self) -> int:
        return self.com_object.ResponseTimeout

    @response_timeout.setter
    def response_timeout(self, value: int):
        self.com_object.ResponseTimeout = value

    @property
    def seed_and_key_active(self) -> bool:
        return self.com_object.SeedAndKeyActive

    @seed_and_key_active.setter
    def seed_and_key_active(self, value: bool):
        self.com_object.SeedAndKeyActive = value

    @property
    def seed_and_key_active_cal(self) -> bool:
        return self.com_object.SeedAndKeyActiveCAL

    @seed_and_key_active_cal.setter
    def seed_and_key_active_cal(self, value: bool):
        self.com_object.SeedAndKeyActiveCAL = value

    @property
    def seed_and_key_file_name(self) -> str:
        return self.com_object.SeedAndKeyFileName

    @seed_and_key_file_name.setter
    def seed_and_key_file_name(self, value: str):
        self.com_object.SeedAndKeyFileName = value

    @property
    def seed_and_key_file_name_cal(self) -> str:
        return self.com_object.SeedAndKeyFileNameCAL

    @seed_and_key_file_name_cal.setter
    def seed_and_key_file_name_cal(self, value: str):
        self.com_object.SeedAndKeyFileNameCAL = value

    @property
    def seed_and_key_on_demand(self) -> bool:
        return self.com_object.SeedAndKeyOnDemand

    @seed_and_key_on_demand.setter
    def seed_and_key_on_demand(self, value: bool):
        self.com_object.SeedAndKeyOnDemand = value

    @property
    def use_ccp_v2_0(self) -> bool:
        return self.com_object.UseCCP_V2_0

    @use_ccp_v2_0.setter
    def use_ccp_v2_0(self, value: bool):
        self.com_object.UseCCP_V2_0 = value

    @property
    def use_daq_timestamps_of_ecu(self) -> bool:
        return self.com_object.UseDAQTimestampsOfECU

    @use_daq_timestamps_of_ecu.setter
    def use_daq_timestamps_of_ecu(self, value: bool):
        self.com_object.UseDAQTimestampsOfECU = value

    @property
    def use_daq_timestamps_of_ecu_div_operator(self) -> bool:
        return self.com_object.UseDAQTimestampsOfECUDivOperator




class McCANSettings:
    """
    The McCANSettings object contains all CAN related XCP/CCP settings.
    """
    def __init__(self, com_object) -> None:
        self.com_object = win32com.client.Dispatch(com_object)

    @property
    def app_channel(self) -> int:
        return self.com_object.AppChannel

    @property
    def request_id(self) -> int:
        return self.com_object.RequestID

    @property
    def response_id(self) -> int:
        return self.com_object.ResponseID

    @property
    def use_bitrate_switc(self) -> bool:
        return self.com_object.UseBitrateSwitch

    @use_bitrate_switc.setter
    def use_bitrate_switc(self, value: bool):
        self.com_object.UseBitrateSwitch = value

    @property
    def use_can_fd(self) -> bool:
        return self.com_object.UseCanFD

    @use_can_fd.setter
    def use_can_fd(self, value: bool):
        self.com_object.UseCanFD = value

    @property
    def use_max_dlc(self) -> bool:
        return self.com_object.UseMaxDLC


class McEthernetSettings:
    """
    The McEthernetSettings object contains all Ethernet related XCP/CCP settings.
    """
    def __init__(self, com_object) -> None:
        self.com_object = win32com.client.Dispatch(com_object)

    @property
    def host(self) -> str:
        return self.com_object.Host

    @property
    def port(self) -> int:
        return self.com_object.Port

    @property
    def tcp(self) -> bool:
        return self.com_object.Tcp


class McFlexRaySettings:
    """
    The McFlexRaySettings object contains all FlexRay related XCP/CCP settings.
    """
    def __init__(self, com_object) -> None:
        self.com_object = win32com.client.Dispatch(com_object)

    @property
    def additional_buffer_count(self) -> int:
        return self.com_object.AdditionalBufferCount

    @property
    def app_channel(self) -> int:
        return self.com_object.AppChannel

    @property
    def dto_buffer(self) -> int:
        return self.com_object.DtoBuffer

    @property
    def min_buffer_count(self) -> int:
        return self.com_object.MinBufferCount

    @property
    def node_address(self) -> bool:
        return self.com_object.NodeAddress


class McMeasurementGroups:
    """
    The McMeasurementGroups object represents all sets of parameters and their measurement settings that can be activated for CCP/XCP measurements.
    """
    def __init__(self, com_object) -> None:
        self.com_object = win32com.client.Dispatch(com_object)

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int) -> 'McMeasurementGroup':
        return McMeasurementGroup(self.com_object.Item(index))

    def add(self, name: str) -> 'McMeasurementGroup':
        return McMeasurementGroup(self.com_object.Add(name))

    def remove(self, index: int):
        self.com_object.Remove(index)


class McMeasurementGroup:
    """
    The McMeasurementGroup object represents a set of parameters and their measurement settings that can be activated for CCP/XCP measurements.
    """
    def __init__(self, com_object) -> None:
        self.com_object = win32com.client.Dispatch(com_object)

    @property
    def active(self) -> bool:
        return self.com_object.Active

    @property
    def name(self) -> str:
        return self.com_object.Name

    @name.setter
    def name(self, value: str):
        self.com_object.Name = value

    @property
    def parameters(self) -> 'McParameters':
        return McParameters(self.com_object.Parameters)

    def activate(self):
        self.com_object.Activate()

    def begin_update(self):
        self.com_object.BeginUpdate()

    def end_update(self):
        self.com_object.EndUpdate()


class McParameters:
    """
    The McParameters object represents all parameters of the database.
    """
    def __init__(self, com_object) -> None:
        self.com_object = win32com.client.Dispatch(com_object)

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int) -> 'McParameter':
        return McParameter(self.com_object.Item(index))


class McParameter:
    """
    The McParameter object represents a parameter of the database.
    """
    def __init__(self, com_object) -> None:
        self.com_object = win32com.client.Dispatch(com_object)

    @property
    def auto_read(self) -> bool:
        return self.com_object.AutoRead

    @auto_read.setter
    def auto_read(self, value: bool):
        self.com_object.AutoRead = value

    @property
    def configured(self) -> bool:
        return self.com_object.Configured

    @configured.setter
    def configured(self, value: bool):
        self.com_object.Configured = value

    @property
    def event_cycle(self) -> int:
        return self.com_object.EventCycle

    @event_cycle.setter
    def event_cycle(self, value: int):
        self.com_object.EventCycle = value

    @property
    def name(self) -> str:
        return McECU(self.com_object.Name)

    @property
    def read_mode(self) -> int:
        return self.com_object.ReadMode

    @read_mode.setter
    def read_mode(self, mode: int):
        self.com_object.ReadMode = mode
