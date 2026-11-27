from py_canoe.core.com_session import dispatch_com_object

from .available_modules import AvailableModules
from .configured_modules import ConfiguredChannel, ConfiguredModule, ConfiguredModules
from .connected_modules import ConnectedModules
from .network_adapters import NetworkAdapters


class VTSystem:
	"""
	Represents the VT System configuration in CANoe.
	"""
	def __init__(self, vt_system_com_object) -> None:
		self.com_object = dispatch_com_object(vt_system_com_object)

	@property
	def available_modules(self) -> AvailableModules:
		"""Collection of known module types which can be added to VT System."""
		return AvailableModules(self.com_object.AvailableModules)

	@property
	def configured_modules(self) -> ConfiguredModules:
		"""Collection of VT System modules currently configured in CANoe."""
		return ConfiguredModules(self.com_object.ConfiguredModules)

	@property
	def connected_modules(self) -> ConnectedModules:
		"""Collection of VT System modules currently connected to the computer."""
		return ConnectedModules(self.com_object.ConnectedModules)

	@property
	def module_description_folder(self) -> str:
		"""Absolute path to the folder where CANoe stores VT System module description files."""
		return self.com_object.ModuleDescriptionFolder

	@property
	def network_adapters(self) -> NetworkAdapters:
		"""Collection of available network adapters for VT System communication."""
		return NetworkAdapters(self.com_object.NetworkAdapters)

	@property
	def selected_network_adapter_id(self) -> int:
		"""ID of the network adapter used for VT System communication."""
		return self.com_object.SelectedNetworkAdapterID

	@selected_network_adapter_id.setter
	def selected_network_adapter_id(self, value: int):
		self.com_object.SelectedNetworkAdapterID = value

	def adapt_to_hardware(self):
		"""Adapts the VT System configuration to the actually connected modules."""
		self.com_object.AdaptToHardware()

	def export_configuration(self, file_name: str):
		"""Exports the current VT System configuration to a VTCFG file."""
		self.com_object.ExportConfiguration(file_name)

	def import_configuration(self, file_name: str, mode: int):
		"""Imports a previously exported VTCFG file. Mode: 0=Merge, 1=Replace."""
		self.com_object.ImportConfiguration(file_name, mode)

	def import_module_description(self, file_name: str):
		"""Imports a module description XML file into CANoe."""
		self.com_object.ImportModuleDescription(file_name)

	def new_configuration_from_hardware(self):
		"""Creates a new configuration matching the currently connected VT System modules."""
		self.com_object.NewConfigurationFromHardware()

	def set_all_modules_offline(self):
		"""Switches all configured modules to offline mode."""
		self.com_object.SetAllModulesOffline()

	def set_all_modules_online(self):
		"""Switches all configured modules to online mode."""
		self.com_object.SetAllModulesOnline()

	def get_channel_by_name(self, channel_name: str) -> ConfiguredChannel:
		"""Returns a ConfiguredChannel object for the given channel name."""
		return ConfiguredChannel(self.com_object.GetChannelByName(channel_name))

	def get_module_by_name(self, module_name: str) -> ConfiguredModule:
		"""Returns a ConfiguredModule object for the given module name."""
		return ConfiguredModule(self.com_object.GetModuleByName(module_name))
