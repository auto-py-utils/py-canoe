class PyCanoeError(Exception):
    """Base exception for py_canoe errors."""
    pass


class NamespaceNotFoundError(PyCanoeError):
    """Raised when a requested namespace does not exist."""
    pass


class ConfigurationNotLoadedError(PyCanoeError):
    """Raised when no configuration is loaded or simulation setup is inaccessible."""
    pass
