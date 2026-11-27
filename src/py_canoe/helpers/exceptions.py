class PyCanoeError(Exception):
    """Base exception for py_canoe errors."""


class NamespaceNotFoundError(PyCanoeError):
    """Raised when a requested namespace does not exist."""


class ConfigurationNotLoadedError(PyCanoeError):
    """Raised when no configuration is loaded or simulation setup is inaccessible."""
