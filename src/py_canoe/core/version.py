from py_canoe.helpers.common import logger


class Version:
    """
    The Version object represents the version of the CANoe application.
    """
    def __init__(self, app):
        self.com_object = app.com_object.Version

    def __str__(self):
        return f"{self.full_name}"

    @property
    def build(self):
        return self.com_object.Build

    @property
    def full_name(self):
        return self.com_object.FullName

    @property
    def major(self):
        return self.com_object.major

    @property
    def minor(self):
        return self.com_object.minor

    @property
    def name(self):
        return self.com_object.Name

    @property
    def patch(self):
        return self.com_object.Patch

    def get_canoe_version_info(self) -> dict[str, str | int]:
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
