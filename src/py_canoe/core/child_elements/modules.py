from collections.abc import Iterator

from py_canoe.core.com_session import dispatch_com_object
from py_canoe.helpers.common import logger


class Modules:
    """The Modules object represents the modules of a test module in CANoe's test setup or a node in CANoe's Simulation Setup / System and Communication Setup."""
    def __init__(self, modules_com_obj):
        self.com_object = modules_com_obj

    @property
    def count(self) -> int:
        return self.com_object.Count

    def iter_items(self) -> Iterator['Module']:
        for index in range(1, self.count + 1):
            yield Module(self.com_object.Item(index))

    def item(self, index: int | None = None) -> 'Module | list[Module]':
        """Returns a Module object from the collection.

        Args:
            index: The 1-based index of the item to retrieve. If None,
                   returns all modules as a list.

        Returns:
            The Module at the given index, or a list of all modules when
            index is None.
        """
        if index is None:
            return list(self.iter_items())
        return Module(self.com_object.Item(index))

    def add(self, full_name: str) -> 'Module':
        """Adds a module to a Modules object.

        Depending on the type of the test node different modules may be added:
        - CAPL test nodes: node layer modules (DLL)
        - .NET or XML test nodes: node layer module (DLL), assemblies (DLL),
          .NET source files (CS), CAPL source files (CAN)

        Args:
            full_name: The path of the module to be added. The path may be
                       absolute or relative to "<configuration path>\\exec32"
                       or "<CANoe path>\\exec32".

        Returns:
            The newly created Module object.

        Note on CANoe run mechanism (32-bit / 64-bit DLL):
            CANoe has two independent concepts:

            - **CANoe application process** (``CANoe64.exe`` / ``CANoe32.exe``):
              the GUI process itself. Its bitness can differ from the RT kernel.
            - **RT Kernel (real-time kernel) architecture**: the execution
              environment that runs CAPL programs and loads external DLLs
              (node layer modules / test modules). Its bitness is stored in
              the configuration and **decides which DLLs can be loaded**:

              - 32-bit RT Kernel → only **32-bit DLLs** can be loaded
              - 64-bit RT Kernel → only **64-bit DLLs** can be loaded

            The program and DLL must have the same bitness. If ``add()`` fails
            or the module cannot be used even though the DLL bitness matches the
            RT kernel, check the RT kernel architecture via
            ``CANoe.get_rt_kernel_architecture()`` /
            ``CANoe.set_rt_kernel_architecture()``
            (``0 = cWin32``, ``1 = cWin64``) and make sure the DLL matches.

            The 32-bit RT kernel is used by default. Existing configurations
            may use either variant. The variant is stored in the configuration
            file and can also be overridden with the
            ``EnforceRtkTargetArchitecture`` switch in ``CAN.ini`` (``[SYSTEM]``
            section: ``0`` = use config, ``1`` = force 32-bit, ``2`` = force
            64-bit).
        """
        module = Module(self.com_object.Add(full_name))
        logger.info(f'Modules: added module "{full_name}" as "{module.name}".')
        return module

    def remove(self, index: int):
        self.com_object.Remove(index)
        logger.info(f'Modules: removed module at index/name "{index}".')


class Module:
    """The Module object represents the modules within a test module in CANoe's test setup or a node of the Simulation Setup / System and Communication Setup of the CANoe application."""
    def __init__(self, module_com_obj):
        self.com_object = dispatch_com_object(module_com_obj)

    @property
    def enabled(self) -> bool:
        return self.com_object.Enabled

    @enabled.setter
    def enabled(self, value: bool):
        self.com_object.Enabled = value

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
    def references(self) -> 'References':
        return References(self.com_object.References)


class References:
    """The References object represents assemblies that are used by a .NET test library."""
    def __init__(self, references_com_obj):
        self.com_object = references_com_obj

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int) -> 'Reference':
        return Reference(self.com_object.Item(index))

    def add(self, full_name: str) -> 'Reference':
        return Reference(self.com_object.Add(full_name))

    def remove(self, index: int):
        self.com_object.Remove(index)


class Reference:
    """The Reference object represents a component that is used by a .NET test library module."""
    def __init__(self, reference_com_obj):
        self.com_object = dispatch_com_object(reference_com_obj)

    @property
    def full_name(self) -> str:
        return self.com_object.FullName

    @property
    def name(self) -> str:
        return self.com_object.Name

    @property
    def path(self) -> str:
        return self.com_object.Path
