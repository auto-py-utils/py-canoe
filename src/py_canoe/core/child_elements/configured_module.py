

class ConfiguredModule:
    """
    Python wrapper for CANoe COM ConfiguredModule object.
    Represents a VT System module in the current configuration.
    """
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def channels(self):
        return self.com_object.Channels

    @property
    def comment(self):
        return self.com_object.Comment

    @comment.setter
    def comment(self, value):
        self.com_object.Comment = value

    @property
    def connectors(self):
        return self.com_object.Connectors

    @property
    def internal_voltage(self):
        return self.com_object.InternalVoltage

    @property
    def is_offline(self):
        return self.com_object.IsOffline

    @property
    def lvds_voltage(self):
        return self.com_object.LVDSVoltage

    @property
    def lvds_voltage_output_enabled(self):
        return self.com_object.LVDSVoltageOutputEnabled

    @property
    def measurement_values(self):
        return self.com_object.MeasurementValues

    @property
    def name(self):
        return self.com_object.Name

    @name.setter
    def name(self, value):
        self.com_object.Name = value

    @property
    def piggy_type(self):
        return self.com_object.PiggyType

    @property
    def pin_labels(self):
        return self.com_object.PinLabels

    @property
    def relay_constraints(self):
        return self.com_object.RelayConstraints

    @property
    def start_state(self):
        return self.com_object.StartState

    @property
    def type(self):
        return self.com_object.Type

    @property
    def user_measurement_values(self):
        return self.com_object.UserMeasurementValues

    @property
    def value_constraints(self):
        return self.com_object.ValueConstraints
