from pathlib import Path

import win32com.client
import win32com.client.gencache
import pythoncom

from py_canoe.core.bus import Bus
from py_canoe.core.capl import Capl
from py_canoe.core.configuration import Configuration
from py_canoe.core.environment import Environment
from py_canoe.core.measurement import Measurement
from py_canoe.core.message_filter import COMRetryMessageFilter
from py_canoe.core.networks import Networks
from py_canoe.core.system import System
from py_canoe.core.ui import Ui
from py_canoe.core.version import Version
from py_canoe.helpers.common import DoEventsUntil, logger


class ApplicationEvents:
    def __init__(self) -> None:
        self.OPENED: bool = False
        self.QUIT: bool = False
        self.CANOE_CFG_FULLNAME: str = ""

    def OnOpen(self, fullname: str) -> None:
        self.CANOE_CFG_FULLNAME = fullname
        self.OPENED = True

    def OnQuit(self) -> None:
        self.QUIT = True


class Application:
    """Main interface to CANoe via COM automation.

    The Application class automatically registers an IMessageFilter that suppresses
    'Server Busy' dialogs when CANoe is temporarily unable to process COM calls
    (e.g., during report generation after measurement stop). Rejected calls are
    retried automatically with exponential backoff up to 60 seconds.
    """

    def __init__(self, enable_events: bool = True) -> None:
        self._enable_events = enable_events
        self.bus_types = {'CAN': 1, 'J1939': 2, 'TTP': 4, 'LIN': 5, 'MOST': 6, 'Kline': 14}
        self.com_object = None
        self.application_events = None
        self.bus: Bus = None
        self.capl: Capl = None
        self.configuration: Configuration = None
        self.environment: Environment = None
        self.measurement: Measurement = None
        self.system: System = None
        self.ui: Ui = None
        self.version: Version = None
        self.capl_function_objects = object()
        self.user_capl_functions = tuple()
        # Register IMessageFilter to suppress "Server Busy" dialogs and auto-retry
        # rejected COM calls. The filter stays active for the Application's lifetime.
        self._message_filter = COMRetryMessageFilter()
        self._message_filter.register()

    @property
    def full_name(self) -> str:
        return self.com_object.FullName

    @property
    def name(self) -> str:
        return self.com_object.Name

    @property
    def path(self) -> str:
        return self.com_object.Path

    @property
    def visible(self) -> bool:
        return self.com_object.Visible

    @visible.setter
    def visible(self, visible: bool) -> None:
        self.com_object.Visible = visible

    def _common_between_pre_and_post_cfg_open(self) -> None:
        self.bus = Bus(self)
        self.capl = Capl(self)
        self.configuration = Configuration(self)
        self.environment = Environment(self)
        self.networks = Networks(self)
        self.system = System(self)
        self.ui = Ui(self)
        self.version = Version(self)

    def _launch_application(self) -> None:
        try:
            # We use gencache.EnsureDispatch to connect to the CANoe COM object.
            # This is preferred over Dispatch or DispatchEx for a few reasons:
            # 1. It connects to a running instance of CANoe if one exists, and
            #    starts a new instance if one is not running. This is the desired
            #    behavior for both attaching to an existing session and starting a new one.
            # 2. It enables early binding by generating a static proxy in the gencache,
            #    which can improve performance.
            # DispatchEx is not used because it would always start a new instance,
            # which is not what we want for the 'attach' functionality.
            self.com_object = win32com.client.gencache.EnsureDispatch("CANoe.Application")
            if self._enable_events:
                self.application_events = win32com.client.WithEvents(self.com_object, ApplicationEvents)
            else:
                self.application_events = ApplicationEvents()
            self.measurement = Measurement(self, enable_events=self._enable_events)
            self.capl_function_objects = lambda: self.measurement.measurement_events.CAPL_FUNCTION_OBJECTS
            self.measurement.measurement_events.CAPL_FUNCTION_NAMES = self.user_capl_functions
            self._common_between_pre_and_post_cfg_open()
        except Exception as e:
            logger.error(f"Failed to launch CANoe application: {e}")
            raise

    def _setup_post_configuration_loading(self) -> None:
        try:
            self._common_between_pre_and_post_cfg_open()
            self.networks.fetch_diagnostic_devices()
            self.configuration.fetch_test_modules()
            self.configuration.fetch_test_units()
        except Exception as e:
            logger.error(f"Error initializing objects after loading configuration: {e}")

    def new(self, auto_save: bool = False, prompt_user: bool = False, timeout: int = 5) -> bool:
        """Create a new empty CANoe configuration."""
        self._launch_application()
        status = False
        try:
            logger.info("Opening new empty CANoe configuration...")
            self.com_object.New(auto_save, prompt_user)
            if self._enable_events:
                cond = lambda: self.application_events.OPENED
            else:
                cond = lambda: self.com_object.FullName != ""
            status = DoEventsUntil(cond, timeout, "New CANoe configuration")
            if status:
                logger.info("New empty CANoe configuration Opened ")
                self._setup_post_configuration_loading()
            return status
        except Exception as e:
            logger.error(f"Error creating new configuration: {e}")
            status = False
            return status

    def open(self, canoe_cfg: str | Path, visible: bool = True, auto_save: bool = True, prompt_user: bool = False, timeout: int = 5) -> bool:
        """Open an existing CANoe configuration."""
        self._launch_application()
        status = False
        try:
            self.visible = visible
            logger.info("Opening CANoe configuration ...")
            canoe_cfg_str = str(canoe_cfg)
            self.com_object.Open(canoe_cfg, auto_save, prompt_user)
            if self._enable_events:
                cond = lambda: self.application_events.OPENED
            else:
                cond = lambda: self.com_object.FullName.lower() == canoe_cfg_str.lower()
            status = DoEventsUntil(cond, timeout, "Open CANoe configuration")
            if status:
                logger.info(f"CANoe Configuration {canoe_cfg} Opened ")
                self._setup_post_configuration_loading()
            return status
        except Exception as e:
            logger.error(f"Error opening configuration: {e}")
            status = False
            return status

    def quit(self, timeout: int = 5) -> bool:
        """Quit CANoe and clean up COM references."""
        status = False
        try:
            self.configuration.modified = False
            self.com_object.Quit()
            status = DoEventsUntil(lambda: self.application_events.QUIT, timeout, "Quit CANoe application")
            if status:
                logger.info("CANoe Application Quit Successfully ")
            return status
        except Exception as e:
            logger.error(f"Error during CANoe quit: {e}")
            status = False
            return status

    def attach_to_active_application(self) -> bool:
        """Attach to a active instance of the CANoe application."""
        try:
            self._launch_application()
            if self.com_object:
                logger.info("Successfully attached to active CANoe application ")
                self._setup_post_configuration_loading()
                return True
            else:
                logger.error("Failed to attach to active CANoe application")
                return False
        except Exception as e:
            logger.error(f"Error attaching to active CANoe application: {e}")
            return False

    def open_config(self, canoe_cfg: str | Path, auto_save: bool = True, prompt_user: bool = False, timeout: int = 60) -> bool:
        """Switch to a different CANoe configuration without restarting CANoe.

        This method switches configurations in an already-running CANoe instance.
        Use this when CANoe is already running and you want to load a different .cfg file.

        For starting CANoe with a configuration from scratch, use open() instead.

        Args:
            canoe_cfg: Path to the CANoe configuration (.cfg) file.
            auto_save: If True, automatically save the current configuration before switching.
            prompt_user: If True, prompt user for confirmation before switching.
            timeout: Maximum time to wait for configuration to load (seconds).

        Returns:
            True if configuration was successfully loaded, False otherwise.
        """
        import time as _time
        status = False
        try:
            abs_path = str(Path(canoe_cfg).resolve())
            logger.info(f"Switching to CANoe configuration: {abs_path}")

            # Reset OPENED flag before calling Open
            self.application_events.OPENED = False

            # Call COM Open() to switch configuration
            self.com_object.Open(abs_path, auto_save, prompt_user)

            if self._enable_events:
                status = DoEventsUntil(
                    lambda: self.application_events.OPENED and
                            self.configuration.full_name.lower() == abs_path.lower(),
                    timeout,
                    f"Switch to configuration {canoe_cfg}"
                )
            else:
                # Poll FullName without PumpWaitingMessages
                poll_deadline = _time.monotonic() + timeout
                while _time.monotonic() < poll_deadline:
                    try:
                        if self.configuration.full_name.lower() == abs_path.lower():
                            status = True
                            break
                    except Exception:
                        pass
                    _time.sleep(0.2)

            if status:
                logger.info(f"Configuration switched successfully to {canoe_cfg}")
                self._setup_post_configuration_loading()
            else:
                logger.warning(f"Configuration switch timed out after {timeout}s")

            return status
        except Exception as e:
            logger.error(f"Error switching configuration: {e}")
            return False

    def pump_messages(self) -> None:
        """Pump COM messages to prevent blocking.

        This is a thin wrapper around pythoncom.PumpWaitingMessages().
        Use this in custom wait loops to keep COM responsive.

        Example:
            >>> while not ready():
            >>>     app.pump_messages()
            >>>     time.sleep(0.1)
        """
        pythoncom.PumpWaitingMessages()
