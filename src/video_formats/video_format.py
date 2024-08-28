import json
import os

from utils.json_exceptions import JSONConfigurationError


class VideoFormat:
    def __init__(self, config_path="../../config/video_format.json"):
        self.config_path = config_path
        self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(
                f"Configuration file not found at {self.config_path}"
            )

        try:
            with open(self.config_path, "r") as file:
                config = json.load(file)
        except json.JSONDecodeError as e:
            raise JSONConfigurationError(
                f"Error parsing the configuration file: {str(e)}"
            )

        video_format_config = self.get_format_config(config)
        if not video_format_config:
            raise JSONConfigurationError(
                f"{self.format_name} configuration section is missing in the configuration file."
            )

        # Set values from config file
        self.intro_duration = video_format_config.get("intro_duration", None)
        self.outro_duration = video_format_config.get("outro_duration", None)
        self.video_segment_duration = video_format_config.get(
            "video_segment_duration", None
        )
        self.intro_initial_silence = video_format_config.get(
            "intro_initial_silence", None
        )
        self.outro_initial_silence = video_format_config.get(
            "outro_initial_silence", None
        )
        self.video_segment_initial_silence = video_format_config.get(
            "video_segment_initial_silence", None
        )

        self.validate_fields()

    def get_format_config(self, config):
        """This method should be overridden in subclasses."""
        raise NotImplementedError(
            "Subclasses should implement this method to return format-specific configuration."
        )

    def validate_fields(self, config=None):
        """Helper method to validate the fields and raise a single exception for all errors."""
        fields = self.get_config() if not config else config
        errors = []  # Collect all errors

        for field_name, value in fields.items():
            if value is None:
                errors.append(f"Missing required field: {field_name}")
            elif not isinstance(value, (int, float)):
                errors.append(
                    f"Invalid type for field '{field_name}': expected int or float, got {type(value).__name__}"
                )
            elif value < 0:
                errors.append(
                    f"Invalid value for field '{field_name}': expected a non-negative number, got {value}"
                )

        if errors:
            raise JSONConfigurationError(
                f"Configuration validation failed with the following errors: {'\n'.join(errors)}"
            )

    def get_config(self):
        return {
            "intro_duration": self.intro_duration,
            "outro_duration": self.outro_duration,
            "video_segment_duration": self.video_segment_duration,
            "intro_initial_silence": self.intro_initial_silence,
            "outro_initial_silence": self.outro_initial_silence,
            "video_segment_initial_silence": self.video_segment_initial_silence,
        }
