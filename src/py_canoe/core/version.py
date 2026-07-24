from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from py_canoe.core.application import Application
from py_canoe.helpers.common import logger


class Version:
    """
    The Version object represents the version of the CANoe application.
    """
    def __init__(self, app: 'Application'):
        self.com_object = app.com_object.Version

    def __str__(self):
        return f"{self.full_name}"

    @property
    def build(self):
        """Return the build number of the CANoe application."""
        return self.com_object.Build

    @property
    def full_name(self):
        """Return the full name of the CANoe application, including version and build information."""
        return self.com_object.FullName

    @property
    def major(self):
        """Return the major version number of the CANoe application."""
        return self.com_object.major

    @property
    def minor(self):
        """Return the minor version number of the CANoe application."""
        return self.com_object.minor

    @property
    def name(self):
        """Return the name of the CANoe application."""
        return self.com_object.Name

    @property
    def patch(self):
        """Return the patch version number of the CANoe application."""
        return self.com_object.Patch

    def get_canoe_version_info(self) -> dict[str, str | int]:
        """Return the version information of the CANoe application."""
        try:
            version_info = {
                'full_name': self.full_name,
                'name': self.name,
                'major': self.major,
                'minor': self.minor,
                'build': self.build,
                'patch': self.patch
            }
            logger.info('CANoe Version Information:')
            for key, value in version_info.items():
                logger.info(f"    {key}: {value}")
            return version_info
        except Exception as e:
            logger.error(f"Error retrieving CANoe version information: {e}")
            return {}
