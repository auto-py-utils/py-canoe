import sys
from pathlib import Path
from typing import Any

import pythoncom
import win32com
import win32com.client
from win32com.client import gencache

from py_canoe.core.capl import Capl
from py_canoe.core.child_elements.bus import Bus
from py_canoe.core.com_session import (
    ComEventSinkProxy,
    ComObjectProxy,
    ComSession,
    ComSessionClosedError,
    StaleComReferenceError,
    with_com_events,
)
from py_canoe.core.configuration import Configuration
from py_canoe.core.environment import Environment
from py_canoe.core.measurement import Measurement
from py_canoe.core.networks import Networks
from py_canoe.core.performance import Performance
from py_canoe.core.simulation import Simulation
from py_canoe.core.system import System
from py_canoe.core.ui import Ui
from py_canoe.core.version import Version
from py_canoe.helpers.bus_type import BusType
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
    """
    Main interface to CANoe Application via COM automation.
    """

    def __init__(self, enable_events: bool = True) -> None:
        self.CANOE_APP_NAME = "CANoe.Application"
        self._enable_events = enable_events
        self.com_object: Any = None
        self.application_events: ApplicationEvents | Any = None
        self._com_session: ComSession | None = None
        self.capl_function_objects = object()
        self.user_capl_functions = ()
        # Lazy wrapper caches: only the wrappers that hold mutable state fetched
        # from CANoe are cached as singletons:
        #   - Measurement registers a COM event sink (WithEvents) that must stay
        #     alive and unique for the Application's lifetime.
        #   - Configuration and Networks cache configuration-scoped data and are
        #     re-created on each configuration load.
        # All other wrappers are stateless facades over read-only COM properties
        # and are created on demand.
        self._configuration: Configuration | None = None
        self._networks: Networks | None = None
        self._measurement: Measurement | None = None

    @property
    def full_name(self) -> str:
        """Returns full path of the currently loaded CANoe configuration."""
        return self.com_object.FullName

    @property
    def name(self) -> str:
        """Returns name of the currently loaded CANoe configuration."""
        return self.com_object.Name

    @property
    def path(self) -> str:
        """Returns the directory path of the currently loaded CANoe configuration."""
        return self.com_object.Path

    @property
    def visible(self) -> bool:
        """Returns whether the CANoe application window is visible."""
        return self.com_object.Visible

    @visible.setter
    def visible(self, visible: bool) -> None:
        """Set the visibility of the CANoe application window."""
        self.com_object.Visible = visible

    @property
    def channel_mapping_name(self) -> str:
        """Sets or returns the application name used to map application channels to
        real existing Vector network interface channels."""
        return self.com_object.ChannelMappingName

    @channel_mapping_name.setter
    def channel_mapping_name(self, name: str) -> None:
        self.com_object.ChannelMappingName = name

    def bus(self, bus_type: BusType = BusType.CAN) -> Bus:
        """Returns a Bus object for the given bus type.

        This mirrors the COM Application.Bus([type]) property. The Bus wrapper is
        stateless (it only wraps the COM Bus object), so a fresh wrapper is
        created on each call.

        Args:
            bus_type: The bus type as a BusType enum member. Defaults to BusType.CAN.
        """
        return Bus(self.com_object.GetBus(bus_type.name))

    @property
    def capl(self) -> Capl:
        """Returns the CAPL object (read-only, mirrors COM Application.CAPL)."""
        return Capl(self)

    @property
    def configuration(self) -> Configuration:
        """Returns the Configuration object (read-only, mirrors COM Application.Configuration).

        The wrapper is cached because it lazily caches test environment and
        configuration data for later calls.
        """
        if self._configuration is None:
            self._configuration = Configuration(self)
        return self._configuration

    @property
    def environment(self) -> Environment:
        """Returns the Environment object (read-only, mirrors COM Application.Environment)."""
        return Environment(self)

    @property
    def measurement(self) -> Measurement:
        """Returns the Measurement object (read-only, mirrors COM Application.Measurement).

        The wrapper is cached because it registers a COM event sink that must
        stay alive and unique for the Application's lifetime.
        """
        if self._measurement is None:
            self._measurement = Measurement(self, enable_events=self._enable_events)
            self._measurement.measurement_events.CAPL_FUNCTION_NAMES = self.user_capl_functions
            self.capl_function_objects = lambda: self._measurement.measurement_events.CAPL_FUNCTION_OBJECTS
        return self._measurement

    @property
    def networks(self) -> Networks:
        """Returns the Networks object (read-only, mirrors COM Application.Networks).

        The wrapper is cached because it holds diagnostic devices data that is
        fetched when a configuration is loaded and consumed by later calls.
        """
        if self._networks is None:
            self._networks = Networks(self)
        return self._networks

    @property
    def performance(self) -> Performance:
        """Returns the Performance object (read-only, mirrors COM Application.Performance)."""
        return Performance(self)

    @property
    def simulation(self) -> Simulation:
        """Returns the Simulation object (read-only, mirrors COM Application.Simulation)."""
        return Simulation(self)

    @property
    def system(self) -> System:
        """Returns the System object (read-only, mirrors COM Application.System)."""
        return System(self)

    @property
    def ui(self) -> Ui:
        """Returns the UI object (read-only, mirrors COM Application.UI)."""
        return Ui(self)

    @property
    def version(self) -> Version:
        """Returns the Version object (read-only, mirrors COM Application.Version)."""
        return Version(self)

    def new_configuration_from_yaml(self, configuration_path: str, path_to_yaml_folder: str, scenario_name: str = "") -> None:
        """Creates a new configuration from an existing venvironment.yaml or venvironment-basic.yaml.

        Args:
            configuration_path: The path where the new configuration should be
                located including the configuration name.
            path_to_yaml_folder: The path to the directory which contains the YAML file.
            scenario_name: The scenario for which a configuration should be created.
        """
        self.com_object.NewConfigurationFromYaml(configuration_path, path_to_yaml_folder, scenario_name)

    def _launch_application(self) -> None:
        try:
            if self._com_session is not None and self.com_object is not None:
                return
            if self._com_session is None:
                self._com_session = ComSession()
            logger.info(f"pywin32 gencache path: {win32com.__gen_path__}")
            def create_application():
                try:
                    return gencache.EnsureDispatch(self.CANOE_APP_NAME)
                except AttributeError as error:
                    logger.warning(
                        f"EnsureDispatch AttributeError: {error}; clearing "
                        "generated typelib modules and falling back to Dispatch."
                    )
                    for key in list(sys.modules.keys()):
                        if key.startswith("win32com.gen_py."):
                            del sys.modules[key]
                    return win32com.client.Dispatch(self.CANOE_APP_NAME)

            handle = self._com_session.invoke(create_application)
            self.com_object = ComObjectProxy(self._com_session, handle)
            if self._enable_events:
                self.application_events = with_com_events(
                    self.com_object, ApplicationEvents
                )
            else:
                self.application_events = ApplicationEvents()
            if self.com_object.Configuration.FullName:
                self._setup_post_configuration_loading()
        except Exception as e:
            logger.error(f"Failed to launch CANoe application: {e}")
            raise

    def _setup_post_configuration_loading(self) -> None:
        try:
            if self._com_session is not None and self.com_object is not None:
                self._release_event_sinks()
                (handle,) = self._com_session.invalidate(self.com_object._handle)
                self.com_object = ComObjectProxy(self._com_session, handle)
                if self._enable_events:
                    self.application_events = with_com_events(
                        self.com_object, ApplicationEvents
                    )
                else:
                    self.application_events = ApplicationEvents()
                self._measurement = None
            # Re-create configuration-scoped caches for each loaded configuration.
            self._configuration = None
            self._networks = None
            self.networks.fetch_diagnostic_devices()
        except Exception as e:
            logger.error(f"Error initializing objects after loading configuration: {e}")

    def _release_event_sinks(self, abandon: bool = False) -> None:
        """Disconnect pywin32 event sinks before COM objects become unreachable."""
        visited = set()

        def walk(obj) -> None:
            obj_id = id(obj)
            if obj is None or obj_id in visited:
                return
            visited.add(obj_id)

            if isinstance(obj, ComEventSinkProxy):
                try:
                    if abandon:
                        obj.abandon()
                    else:
                        obj.close()
                except (
                    pythoncom.com_error,
                    ComSessionClosedError,
                    StaleComReferenceError,
                ) as error:
                    logger.warning(f"Error disconnecting COM event sink: {error}")
                return

            if isinstance(obj, ComObjectProxy):
                return

            # Avoid walking into COM proxy wrappers. These wrappers may expose
            # nested attributes that are not owned by our Python object graph
            # and can trigger unsafe COM activity during shutdown.
            if hasattr(obj, "_oleobj_"):
                return

            if isinstance(obj, dict):
                for value in obj.values():
                    walk(value)
                return

            if isinstance(obj, (list, tuple, set)):
                for value in obj:
                    walk(value)
                return

            if not hasattr(obj, "__dict__"):
                return

            for name, value in tuple(vars(obj).items()):
                if value is None or name in {
                    "com_object",
                    "_com_session",
                    "_enable_events",
                }:
                    continue
                if name.endswith("_events") or name == "events":
                    close = getattr(value, "close", None)
                    if callable(close):
                        try:
                            if isinstance(value, ComEventSinkProxy):
                                if abandon:
                                    value.abandon()
                                else:
                                    close()
                            else:
                                close()
                        except pythoncom.com_error as e:
                            # These errors commonly occur when the COM server has already shut down
                            # and Python is still trying to disconnect stale event sink wrappers.
                            if e.hresult in {
                                -2147023170,  # RPC call failed
                                -2147023174,  # RPC server unavailable
                                -2147023175,  # No process is on the other end of the pipe
                                -2147023169,  # The remote procedure call failed. (alternate code)
                            }:
                                logger.debug(f"Stale COM event sink '{name}' disconnected after server shutdown: {e}")
                            else:
                                logger.warning(f"Error disconnecting COM event sink '{name}': {e}")
                        except Exception as e:
                            logger.warning(f"Error disconnecting COM event sink '{name}': {e}")
                    try:
                        setattr(obj, name, None)
                    except Exception as error:
                        logger.debug(f"Could not clear closed COM event sink '{name}': {error}")
                    continue
                walk(value)

        walk(self)

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
                logger.info("New empty CANoe configuration Opened")
                self._setup_post_configuration_loading()
            return status
        except Exception as e:
            logger.error(f"Error creating new configuration: {e}")
            status = False
            return status

    def open(self, canoe_cfg: str | Path, visible: bool = True, auto_save: bool = True, prompt_user: bool = False, timeout: int = 5) -> bool:
        """Open a CANoe configuration file (.cfg) in a new or existing CANoe instance."""
        self._launch_application()
        status = False
        try:
            self.visible = visible
            logger.info("Opening CANoe configuration ...")
            canoe_cfg_str = str(Path(canoe_cfg).resolve())
            self.com_object.Open(canoe_cfg_str, auto_save, prompt_user)
            if self._enable_events:
                cond = lambda: self.application_events.OPENED
            else:
                cond = lambda: self.com_object.FullName.lower() == canoe_cfg_str.lower()
            status = DoEventsUntil(cond, timeout, "Open CANoe configuration")
            if status:
                logger.info(f"CANoe Configuration {canoe_cfg} Opened")
                self._setup_post_configuration_loading()
            return status
        except Exception as e:
            logger.error(f"Error opening configuration: {e}")
            status = False
            return status

    def quit(self, timeout: int = 5) -> bool:
        """Quit the CANoe application gracefully."""
        status = False
        abandon_event_sinks = False
        try:
            if self._configuration is not None and self.configuration.modified:
                self.configuration.modified = False
            # Do NOT release event sinks before Quit(). CANoe fires OnExit (and
            # potentially OnStop) as part of its internal shutdown sequence after
            # Quit() is called. Releasing sinks beforehand leaves CANoe with a
            # dangling vtable pointer → access violation → crash dialog.
            # After OnQuit, abandon the sinks instead of calling Unadvise on a
            # server that may already have disconnected.
            if self._com_session is not None and isinstance(
                self.com_object, ComObjectProxy
            ):
                # Release child COM proxies while the server is still reachable.
                (handle,) = self._com_session.invalidate(self.com_object._handle)
                self.com_object = ComObjectProxy(self._com_session, handle)
            self.com_object.Quit()
            status = DoEventsUntil(lambda: self.application_events.QUIT, timeout, "Quit CANoe application")
            if status:
                abandon_event_sinks = True
                logger.info("CANoe Application Quit Successfully.")
            return status
        except Exception as e:
            logger.error(f"Error during CANoe quit: {e}")
            status = False
            return status
        finally:
            self.close(abandon_event_sinks=abandon_event_sinks)

    def close(self, *, abandon_event_sinks: bool = False) -> None:
        """Release or abandon event sinks, then close the COM session."""
        try:
            self._release_event_sinks(abandon=abandon_event_sinks)
        finally:
            session = self._com_session
            self._com_session = None
            self.com_object = None
            self.application_events = None
            if session is not None:
                session.close(abandon_event_sinks=abandon_event_sinks)

    def attach_to_active_application(self) -> bool:
        """Attach to an already running CANoe application instance."""
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
                    lambda: self.application_events.OPENED and self.configuration.full_name.lower() == abs_path.lower(),
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
                    except Exception as error:
                        logger.debug(f"Configuration is not ready during switch polling: {error}")
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
        if self._com_session is not None:
            self._com_session.invoke(pythoncom.PumpWaitingMessages)
