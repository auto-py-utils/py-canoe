from py_canoe.helpers.common import logger

from py_canoe.core.child_elements.write import Write


class Ui:
    """
    The UI object represents the user interface in CANoe.
    """
    def __init__(self, app):
        self.app = app
        self.com_object = self.app.com_object.UI

    def get_command_enabled(self, command: str) -> bool:
        return self.com_object.GetCommandEnabled(command)

    def set_command_enabled(self, command: str, enabled: bool) -> None:
        self.com_object.SetCommandEnabled(command, enabled)

    @property
    def write(self) -> Write:
        return Write(self.com_object.Write)

    def activate_desktop(self, desktop_name: str) -> bool:
        try:
            self.com_object.ActivateDesktop(desktop_name)
            logger.info(f"UI Desktop '{desktop_name}' activated successfully")
            return True
        except Exception as e:
            logger.error(f"Error activating UI Desktop '{desktop_name}': {e}")
            return False

    def create_desktop(self, desktop_name: str) -> bool:
        try:
            if float(f"{self.app.version.major}.{self.app.version.minor}") >= 15.3:
                self.com_object.CreateDesktop(desktop_name)
                logger.info(f"UI Desktop '{desktop_name}' created successfully")
                return True
            else:
                logger.warning(f"Cannot create desktop '{desktop_name}': Requires CANoe version 15.3 or higher.")
                return False
        except Exception as e:
            logger.error(f"Error creating UI Desktop '{desktop_name}': {e}")
            return False

    def open_baudrate_dialog(self) -> bool:
        try:
            self.com_object.OpenBaudrateDialog()
            logger.info("UI Baudrate Dialog opened successfully")
            return True
        except Exception as e:
            logger.error(f"Error opening UI Baudrate Dialog: {e}")
            return False
