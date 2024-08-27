class JSONConfigurationError(Exception):
    """Exception raised for errors in JSON configuration."""

    def __init__(self, message, *args):
        super().__init__(message, *args)

class JSONFileError(Exception):
    """Exception raised for errors in JSON Files."""

    def __init__(self, message, *args):
        super().__init__(message, *args)

class JSONWarning(Warning):
    """Warning raised for non-critical issues in JSON configuration."""

    def __init__(self, message, *args):
        super().__init__(message, *args)
