import win32com.client
from typing import Union, TYPE_CHECKING
if TYPE_CHECKING:
    from py_canoe.core.application import Application

class SimulationEvents:
    """COM event sink for CANoe Simulation events (OnIdle).

    **Not registered by default** (Simulation.__init__ has enable_events=False).
    OnIdle fires on every simulation step — registering this sink while also making
    outgoing COM calls would cause RPC_E_CALL_REJECTED. Only enable if the caller
    pumps the STA message queue continuously (via wait() / PumpWaitingMessages).
    """

    EVENTS_INFORMATION = {}

    @staticmethod
    def OnIdle(timeHigh, time):
        SimulationEvents.EVENTS_INFORMATION['timeHigh'] = timeHigh
        SimulationEvents.EVENTS_INFORMATION['time'] = time


class Simulation:
    """
    The Simulation object represents CANoe's measurement functions in the Simulation mode.
    With the help of the Simulation object you can control the system time from an external source during the measurement.
    CANoe automatically goes into Slave mode at the measurement start if you access the Simulation object.
    """
    def __init__(self, app: 'Application', enable_events: bool = False):
        self.com_object = app.com_object.Simulation
        if enable_events:
            win32com.client.WithEvents(self.com_object, SimulationEvents)

    @property
    def animation(self) -> Union[int, float]:
        """Return the current animation speed of the simulation. The value is a float between 0 and 1, where 0 means no animation and 1 means full animation speed."""
        return self.com_object.Animation

    @animation.setter
    def animation(self, value: Union[int, float]):
        """Set the animation speed of the simulation. The value must be a float between 0 and 1, where 0 means no animation and 1 means full animation speed."""
        self.com_object.Animation = value

    @property
    def current_time(self) ->int:
        """Return the current simulation time in ticks. The value is an integer representing the number of ticks since the start of the simulation."""
        return self.com_object.CurrentTime

    @property
    def current_time_high(self) -> int:
        """Return the high part of the current simulation time in ticks. The value is an integer representing the high part of the number of ticks since the start of the simulation."""
        return self.com_object.CurrentTimeHigh

    @property
    def notification_type(self) -> int:
        """Return the current notification type of the simulation. The value is an integer representing the notification type."""
        return self.com_object.NotificationType

    @notification_type.setter
    def notification_type(self, value: int):
        """Set the notification type of the simulation. The value must be an integer representing the notification type."""
        self.com_object.NotificationType = value

    def increment_time(self, ticks: int):
        """Increment the simulation time by the specified number of ticks."""
        self.com_object.IncrementTime(ticks)

    def increment_time_and_wait(self, ticks: int):
        """Increment the simulation time by the specified number of ticks and wait for the simulation to process the time increment."""
        self.com_object.IncrementTimeAndWait(ticks)
