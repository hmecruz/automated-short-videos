class DurationExceededError(Exception):
    """
    Exception raised when an audio duration exceeds the expected limit.

    This exception is used to signal that an audio segment or the final audio 
    file exceeds the duration that was anticipated based on the configuration 
    settings. 
    """

    def __init__(self, message):
        super().__init__(message)
