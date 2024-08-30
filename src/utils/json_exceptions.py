class JSONConfigurationError(Exception):
    """Exception raised for errors in JSON configuration files."""

    def __init__(self, message, *args):
        super().__init__(message, *args)
        