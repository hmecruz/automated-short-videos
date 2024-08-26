class DurationExceededError(Exception):
    def __init__(self, message):
        super().__init__(message)


class AudioProcessingError(Exception):
    def __init__(self, message):
        super().__init__(message)
