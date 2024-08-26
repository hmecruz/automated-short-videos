import logging
import os


class Logger:
    def __init__(self, log_dir):
        self.log_file_path = os.path.join(log_dir, "errors.log")
        self._setup_logger()
        self.clear_error_log()

    def _setup_logger(self):
        """Set up the logger with a file handler and format."""
        self.logger = logging.getLogger("VideoProcessingLogger")
        self.logger.setLevel(logging.DEBUG)

        # Create a file handler for logging errors
        file_handler = logging.FileHandler(
            self.log_file_path, mode="a", encoding="utf-8"
        )
        file_handler.setLevel(logging.ERROR)

        # Create a console handler for logging debug and higher levels
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Define the logging format
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def log_error(self, message):
        """Log an error message to the file and console."""
        self.logger.error(message)

    def clear_error_log(self):
        """Clear the error log file."""
        open(self.log_file_path, "w", encoding="utf-8").close()


"""
from utils.logger import Logger

# Example usage
log_dir = './logs'
logger = Logger(log_dir)

# Log an error message
logger.log_error('This is an error message.')
"""
