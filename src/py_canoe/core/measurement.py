from typing import Union, TYPE_CHECKING
import time
import win32com.client
import pythoncom
if TYPE_CHECKING:
    from py_canoe.core.application import Application
from py_canoe.core.capl import CaplFunction
from py_canoe.helpers.common import DoEventsUntil
from py_canoe.helpers.common import logger, wait


class MeasurementEvents:
    """COM event sink for CANoe Measurement events (OnStart, OnStop, OnInit, OnExit).

    **STA threading note:** WithEvents registers this sink in the caller's STA thread.
    CANoe delivers callbacks (OnVerdictChanged, OnStop, ...) via that same STA queue.
    If the caller blocks with time.sleep() during measurement — without pumping the
    COM message queue — pending callbacks accumulate. Any outgoing COM call made while
    a callback delivery is pending (e.g. UI.Write.Text) will be rejected with
    RPC_E_CALL_REJECTED ("program is busy").

    Fix: replace time.sleep() with wait() (which calls PumpWaitingMessages) during
    any wait period while measurement is running. This keeps the STA queue drained
    so outgoing COM calls are never rejected.
    """

    def __init__(self):
        self.APP_COM_OBJ = object
        self.INIT: bool = False
        self.START: bool = False
        self.STOP: bool = False
        self.EXIT: bool = False
        self.CAPL_FUNCTION_OBJECTS = dict()
        self.CAPL_FUNCTION_NAMES = tuple()

    def OnInit(self):
        """measurement is initialized"""
        for fun in self.CAPL_FUNCTION_NAMES:
            self.CAPL_FUNCTION_OBJECTS[fun] = CaplFunction(self.APP_COM_OBJ.CAPL.GetFunction(fun))
        self.INIT = True

    def OnStart(self):
        """measurement is started"""
        self.START = True

    def OnStop(self):
        """measurement is stopped"""
        self.STOP = True

    def OnExit(self):
        """measurement is exited"""
        self.CAPL_FUNCTION_OBJECTS.clear()
        self.EXIT = True


class Measurement:
    def __init__(self, app: 'Application', enable_events: bool = True):
        # Use the Application's Measurement object directly - do NOT create a
        # separate Dispatch wrapper. A separate Dispatch creates a different COM
        # proxy that races with the Application's internal proxy, causing
        # "Server Busy" dialogs during concurrent operations.
        self.com_object = app.com_object.Measurement
        self._enable_events = enable_events
        if enable_events:
            self.measurement_events: MeasurementEvents = win32com.client.WithEvents(self.com_object, MeasurementEvents)
            self.measurement_events.APP_COM_OBJ = app.com_object
        else:
            self.measurement_events = MeasurementEvents()
            self.measurement_events.APP_COM_OBJ = app.com_object

    @property
    def animation_delay(self) -> int:
        """Returns the current animation delay in milliseconds."""
        return self.com_object.AnimationDelay

    @animation_delay.setter
    def animation_delay(self, delay: int):
        """Set the animation delay in milliseconds. This controls the speed of the measurement when running in animation mode."""
        self.com_object.AnimationDelay = delay
        logger.info(f"Animation Delay set to: {delay} ms")

    @property
    def measurement_index(self) -> int:
        """Return the current measurement index. The measurement index is an integer that uniquely identifies the current measurement session."""
        index = self.com_object.MeasurementIndex
        logger.info(f"Measurement Index value: {index}")
        return index

    @measurement_index.setter
    def measurement_index(self, index: int):
        """Set the measurement index. The measurement index is an integer that uniquely identifies the current measurement session."""
        self.com_object.MeasurementIndex = index
        logger.info(f"Measurement Index set to: {index}")

    @property
    def running(self) -> bool:
        """Return True if the measurement is currently running, False otherwise."""
        return self.com_object.Running

    def start(self, timeout=30) -> bool:
        """Start the measurement and wait for it to be running. Returns True if the measurement started successfully, False otherwise."""
        try:
            if self.running:
                logger.warning("Measurement is already running")
                return True
            self.measurement_events.START = False
            self.com_object.Start()
            if self._enable_events:
                status = DoEventsUntil(lambda: self.measurement_events.START, timeout, "CANoe Measurement Start")
            else:
                poll_deadline = time.monotonic() + timeout
                status = False
                while time.monotonic() < poll_deadline:
                    if self.com_object.Running:
                        status = True
                        break
                    time.sleep(0.1)
            if status:
                logger.info('Measurement Started')
                # Stabilization wait: CAPL on start{} handlers and network interface
                # initialization continue asynchronously after the measurement begins.
                time.sleep(2)
                logger.info('Measurement stabilization complete')
            return status
        except Exception as e:
            logger.error(f"Error starting CANoe measurement: {e}")
            return False

    def stop(self, timeout=30, post_stop_pump: int = 10) -> bool:
        """Stop the measurement and wait for it to be stopped. Returns True if the measurement stopped successfully, False otherwise."""
        return self.stop_ex(timeout, post_stop_pump=post_stop_pump)

    def stop_ex(self, timeout=30, post_stop_pump: int = 10) -> bool:
        """Stop the measurement and wait for it to be stopped. Returns True if the measurement stopped successfully, False otherwise. Optionally specify a timeout (in seconds) for waiting and a post-stop pump duration (in seconds) to drain COM callbacks after stopping."""
        t0 = time.monotonic()
        if not self.running:
            logger.warning("Measurement is already stopped")
            return True
        logger.info("stop_ex: calling Stop()")
        self.measurement_events.STOP = False
        try:
            # IMessageFilter (registered in Application.__init__) handles busy-retry
            # automatically — no manual retry loop needed here.
            self.com_object.Stop()
            elapsed = round(time.monotonic() - t0, 2)
            logger.info(f"stop_ex: Stop() accepted after {elapsed}s")
        except Exception as e:
            elapsed = round(time.monotonic() - t0, 2)
            logger.error(f"stop_ex: Stop() failed after {elapsed}s: {e}")
            return False
        if self._enable_events:
            status = DoEventsUntil(lambda: self.measurement_events.STOP, timeout, "CANoe Measurement Stop")
        else:
            # Poll Running without PumpWaitingMessages — pumping during post-stop
            # report generation triggers Windows' "not responding" dialog.
            poll_deadline = time.monotonic() + timeout
            status = False
            while time.monotonic() < poll_deadline:
                if not self.com_object.Running:
                    status = True
                    break
                time.sleep(0.1)
        elapsed = round(time.monotonic() - t0, 2)
        if status:
            logger.info(f"stop_ex: Running=False confirmed after {elapsed}s total")
            logger.info('Measurement Stopped')
        else:
            logger.warning(f"stop_ex: Running still True after {elapsed}s — timeout")
        if post_stop_pump > 0:
            logger.info(f"stop_ex: draining COM callbacks for {post_stop_pump}s...")
            for _ in range(post_stop_pump * 10):
                pythoncom.PumpWaitingMessages()
                time.sleep(0.1)
        return status

    def start_measurement_in_animation_mode(self, animation_delay=100, timeout=30) -> bool:
        """Start the measurement in animation mode with a specified animation delay (in milliseconds) and wait for it to start. Returns True if the measurement started successfully, False otherwise."""
        try:
            if self.running:
                logger.warning("Measurement is already running, cannot animate")
                return False
            self.measurement_events.START = False
            self.animation_delay = animation_delay
            self.com_object.Animate()
            status = DoEventsUntil(lambda: self.measurement_events.START, timeout, "CANoe Measurement Animation Initialization")
            if status:
                logger.info(f'Measurement started in Animation mode with animation delay {animation_delay} ms')
            else:
                logger.error(f"Measurement did not start in Animation mode within {timeout} seconds")
            return status
        except Exception as e:
            logger.error(f"Error starting CANoe measurement in animation mode: {e}")
            return False

    def break_measurement_in_offline_mode(self) -> bool:
        """Break the measurement in offline mode. This is typically used to pause the measurement for debugging or analysis purposes. Returns True if the break was applied successfully, False otherwise."""
        try:
            if not self.running:
                logger.warning("Measurement is not running, cannot break")
                return False
            self.com_object.Break()
            logger.info('Measurement break applied in Offline mode')
            return True
        except Exception as e:
            logger.error(f"Error breaking CANoe measurement in offline mode: {e}")
            return False

    def reset_measurement_in_offline_mode(self) -> bool:
        """Reset the measurement in offline mode. This is typically used to reset the measurement state for debugging or analysis purposes. Returns True if the reset was applied successfully, False otherwise."""
        try:
            self.com_object.Reset()
            logger.info('Measurement reset applied in Offline mode')
            return True
        except Exception as e:
            logger.error(f"Error resetting CANoe measurement in offline mode: {e}")
            return False

    def process_measurement_event_in_single_step(self) -> bool:
        """Process the next measurement event in single step mode. This is typically used for debugging or analysis purposes. Returns True if the event was processed successfully, False otherwise."""
        try:
            self.com_object.Step()
            logger.info('Processed a measurement event in single step ')
            return True
        except Exception as e:
            logger.error(f"Error processing CANoe measurement event in single step: {e}")
            return False
