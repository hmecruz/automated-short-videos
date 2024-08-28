from .quiz_format import QuizFormat
from .wyr_format import WYRFormat

# Dictionary to map format names to their respective classes
format_classes = {
    "quiz": QuizFormat,
    "wyr": WYRFormat,
    # Add other formats here as they are implemented
}

def create_video_format_instance(format_name):
    """
    Create an instance of the specified video format class.
    
    :param format_name: The name of the video format (e.g., 'quiz', 'wyr').
    :param config_path: The path to the configuration file, if needed by the format.
    :return: An instance of the requested video format class.
    :raises ValueError: If the format name is not supported.
    """
    if format_name not in format_classes:
        raise ValueError(f"Unsupported video format: {format_name}")
    
    # Instantiate the class, optionally passing the config path if needed
    
    return format_classes[format_name]()