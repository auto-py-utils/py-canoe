
from py_canoe.core.child_elements.configured_module import ConfiguredModule


class ConfiguredModules:
    """
    Python wrapper for CANoe COM ConfiguredModules object.
    Represents the collection of VT System modules currently configured.
    """
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def count(self):
        """Returns the number of modules in the collection."""
        return self.com_object.Count

    def item(self, index) -> 'ConfiguredModule':
        """
        Returns the ConfiguredModule object at the given index (1-based).
        Args:
            index (int): Index of the module (1-based)
        Returns:
            ConfiguredModule COM object
        """
        return ConfiguredModule(self.com_object.Item(index))

    def add_application_specific_module(self, module_id) -> 'ConfiguredModule':
        """
        Adds an application specific module to the configuration.
        Args:
            module_id (int): ID of the application specific module to add
        Returns:
            ConfiguredModule COM object
        """
        return ConfiguredModule(self.com_object.AddApplicationSpecificModule(module_id))

    def add_basic_module(self, module_type) -> 'ConfiguredModule':
        """
        Adds a basic module to the configuration.
        Args:
            module_type (int): Type of the module to add (e.g. 1004)
        Returns:
            ConfiguredModule COM object
        """
        return ConfiguredModule(self.com_object.AddBasicModule(module_type))

    def remove(self, index):
        """
        Removes a single module from the configuration.
        Args:
            index (int): 1-based index of the module to remove
        """
        self.com_object.Remove(index)

    def remove_all(self):
        """
        Removes all modules from the configuration.
        """
        self.com_object.RemoveAll()
