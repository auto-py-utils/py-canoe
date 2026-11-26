from py_canoe.core.com_session import dispatch_com_object


class DiagnosticsSetup:
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def diag_descriptions(self) -> 'DiagDescriptions':
        return DiagDescriptions(self.com_object.DiagDescriptions)


class DiagDescriptions:
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int) -> 'DiagDescription':
        return DiagDescription(self.com_object.Item(index))

    def add(self, network: str, file_path: str, ecu_identifier: str | None=None) -> 'DiagDescription':
        if ecu_identifier is None:
            return DiagDescription(self.com_object.Add(network, file_path))
        else:
            return DiagDescription(self.com_object.AddEx(network, file_path, ecu_identifier))

    def add_diag_access(self, network: str, file_path: str, ecu_identifier: str | None=None) -> 'DiagDescription':
        if ecu_identifier is None:
            return DiagDescription(self.com_object.AddDiagAccess(network, file_path))
        else:
            return DiagDescription(self.com_object.AddDiagAccessEx(network, file_path, ecu_identifier))

    def remove(self, index: int):
        self.com_object.Remove(index)


class DiagDescription:
    def __init__(self, com_object):
        self.com_object = dispatch_com_object(com_object)

    @property
    def additional_descriptions(self) -> 'AdditionalDescriptions':
        return AdditionalDescriptions(self.com_object.AdditionalDescriptions)

    @property
    def diag_variants(self) -> 'DiagVariants':
        return DiagVariants(self.com_object.DiagVariants)

    @property
    def file_path(self) -> str:
        return self.com_object.FilePath

    @property
    def information(self) -> str:
        return self.com_object.Information

    @property
    def interface(self) -> str:
        return self.com_object.Interface

    @interface.setter
    def interface(self, interface_qualifier: str):
        self.com_object.Interface = interface_qualifier

    @property
    def interpretation_order(self) -> 'InterpretationOrder':
        return InterpretationOrder(self.com_object.InterpretationOrder)

    @property
    def language(self) -> str:
        return self.com_object.Language

    @language.setter
    def language(self, value: str):
        self.com_object.Language = value

    @property
    def manual_communication_parameters(self) -> bool:
        return self.com_object.ManualCommunicationParameters

    @property
    def mode(self) -> str:
        return self.com_object.Mode

    @property
    def name(self) -> str:
        return self.com_object.Name

    @property
    def network(self) -> str:
        return self.com_object.Network

    @property
    def node(self) -> str:
        return self.com_object.Node

    @property
    def port(self) -> str:
        return self.com_object.Port

    @port.setter
    def port(self, value: str):
        self.com_object.Port = value

    @property
    def qualifier(self) -> str:
        return self.com_object.Qualifier

    @property
    def seed_n_key_dll(self) -> str:
        return self.com_object.SeedNKeyDLL

    @seed_n_key_dll.setter
    def seed_n_key_dll(self, value: str):
        self.com_object.SeedNKeyDLL = value

    @property
    def variant(self) -> str:
        return self.com_object.Variant

    @variant.setter
    def variant(self, variant_qualifier: str):
        self.com_object.Variant = variant_qualifier

    def close_windows(self, windows: int | None = None):
        if windows is None:
            self.com_object.CloseWindows()
        else:
            self.com_object.CloseWindows(windows)

    def open_windows(self, windows: int | None = None):
        if windows is None:
            self.com_object.OpenWindows()
        else:
            self.com_object.OpenWindows(windows)

    def replace_description_file(self, file_path: str):
        self.com_object.ReplaceDescriptionFile(file_path)


class AdditionalDescriptions:
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int) -> 'AdditionalDescription':
        return AdditionalDescription(self.com_object.Item(index))

    def add(self, file_path: str, ecu_identifier: str | None=None) -> 'AdditionalDescription':
        if ecu_identifier is None:
            return AdditionalDescription(self.com_object.Add(file_path))
        else:
            return AdditionalDescription(self.com_object.AddEx(file_path, ecu_identifier))

    def remove(self, index: int):
        self.com_object.Remove(index)


class AdditionalDescription:
    def __init__(self, com_object):
        self.com_object = dispatch_com_object(com_object)

    @property
    def diag_variants(self) -> 'DiagVariants':
        return DiagVariants(self.com_object.DiagVariants)

    @property
    def file_path(self) -> str:
        return self.com_object.FilePath

    @property
    def master_description(self) -> 'DiagDescription':
        return DiagDescription(self.com_object.MasterDescription)

    @property
    def language(self) -> str:
        return self.com_object.Language

    @language.setter
    def language(self, value: str):
        self.com_object.Language = value

    @property
    def name(self) -> str:
        return self.com_object.Name

    @property
    def qualifier(self) -> str:
        return self.com_object.Qualifier

    @property
    def variant(self) -> str:
        return self.com_object.Variant

    @variant.setter
    def variant(self, variant_qualifier: str):
        self.com_object.Variant = variant_qualifier

    def close_windows(self, windows: int | None = None):
        if windows is None:
            self.com_object.CloseWindows()
        else:
            self.com_object.CloseWindows(windows)

    def open_windows(self, windows: int | None = None):
        if windows is None:
            self.com_object.OpenWindows()
        else:
            self.com_object.OpenWindows(windows)


class DiagVariants:
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int) -> 'DiagVariant':
        return DiagVariant(self.com_object.Item(index))


class DiagVariant:
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def name(self) -> str:
        return self.com_object.Name

    @property
    def qualifier(self) -> str:
        return self.com_object.Qualifier

class InterpretationOrder:
    def __init__(self, com_object):
        self.com_object = com_object

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int) -> 'DiagDescription':
        return DiagDescription(self.com_object.Item(index))

    def move(self, from_index: int, to_index: int):
        self.com_object.Move(from_index, to_index)
