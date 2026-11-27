from py_canoe.core.child_elements.application_model_setup import ApplicationModelSetup
from py_canoe.core.child_elements.data_source_setup import DataSourceSetup
from py_canoe.core.child_elements.vtt_sut_import_result import VttSutImportResult


class CommunicationSetup:
    """
    Provides access to CANoe's System and Communication Setup via COM.
    """
    def __init__(self, com_object) -> None:
        self.com_object = com_object

    @property
    def application_model_setup(self) -> 'ApplicationModelSetup':
        return ApplicationModelSetup(self.com_object.ApplicationModelSetup)

    @property
    def data_source_setup(self) -> 'DataSourceSetup':
        return DataSourceSetup(self.com_object.DataSourceSetup)

    def import_vtt_sut(self, sut_manifest_path: str) -> 'VttSutImportResult':
        return VttSutImportResult(self.com_object.ImportVttSut(sut_manifest_path))
