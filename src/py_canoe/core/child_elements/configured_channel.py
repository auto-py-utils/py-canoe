from py_canoe.core.com_session import dispatch_com_object


class ConfiguredChannel:
    """
    Python wrapper for CANoe COM ConfiguredChannel object.
    Represents a VT System channel in the current configuration.
    """
    def __init__(self, com_object):
        self.com_object = dispatch_com_object(com_object)

    @property
    def comment(self):
        return self.com_object.Comment
    @comment.setter
    def comment(self, value):
        self.com_object.Comment = value

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
    def pin_labels(self):
        return self.com_object.PinLabels

    @property
    def relay_constraints(self):
        return self.com_object.RelayConstraints

    @property
    def start_state(self):
        return self.com_object.StartState

    @property
    def user_measurement_values(self):
        return self.com_object.UserMeasurementValues

    @property
    def value_constraints(self):
        return self.com_object.ValueConstraints
