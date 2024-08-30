from utils.json_exceptions import JSONConfigurationError
from utils.utils import load_json


class VideoFormat:
    """
    A base class representing a video format configuration.

    This class provides methods to load, validate, and retrieve configuration 
    settings for different video formats from a JSON file. Subclasses should 
    define a `format_name` attribute to specify the format they represent.
    """

    def __init__(self):
        """
        Initializes the VideoFormat instance and loads the video format configuration.

        The constructor sets the path to the configuration file and loads the 
        configuration specific to the video format, raising an exception if 
        the configuration is missing or invalid.
        """
        self.config_path = "../config/video_format.json"
        self.load_config()


    def load_config(self):
        """
        Load the video format configuration from a JSON file.

        This method loads the entire configuration from the specified JSON file, 
        retrieves the section relevant to the current video format, and assigns 
        the configuration values to the instance attributes. It also validates 
        that all required fields are present and correctly typed.

        :raises JSONConfigurationError: If the format-specific configuration 
        section is missing or if any required fields are invalid.
        """
        config = load_json(self.config_path)

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

        VideoFormat.validate_fields(self.get_config())

    def get_format_config(self, config: dict):
        """
        Retrieve the configuration specific to the current video format.

        This method returns the configuration dictionary associated with the 
        specific video format instance. The format is identified by the 
        `format_name` attribute of the class.

        :param config: dict
            A dictionary containing various video format configurations.
        
        :return: dict
            A dictionary containing the configuration settings specific to the 
            current video format. If no such settings exist, an empty dictionary 
            is returned.
        """
        return config.get(self.format_name, {})
    
    @staticmethod
    def validate_fields(fields):
        """
        Validate the configuration fields and raise an exception if any are invalid.

        This method checks that all required fields are present, have the correct 
        type (int or float), and are non-negative. It collects any errors found 
        during validation and raises them in a single exception.

        :param fields: dict
            A dictionary of configuration fields to validate.
        
        :raises JSONConfigurationError: If any required fields are missing, 
        have an invalid type, or contain invalid values.
        """
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
        """
        Get the current configuration values as a dictionary.

        This method returns the current configuration values for the video format, 
        including the durations and initial silence periods for intro, outro, and 
        main video segments.

        :return: dict
            A dictionary containing the current configuration settings.
        """
        return {
            "intro_duration": self.intro_duration,
            "outro_duration": self.outro_duration,
            "video_segment_duration": self.video_segment_duration,
            "intro_initial_silence": self.intro_initial_silence,
            "outro_initial_silence": self.outro_initial_silence,
            "video_segment_initial_silence": self.video_segment_initial_silence,
        }
