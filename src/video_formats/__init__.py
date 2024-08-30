from .quiz_format import QuizFormat
from .wyr_format import WYRFormat

# Dictionary to map format names to their respective classes
format_classes = {
    "quiz": QuizFormat,
    "wyr": WYRFormat,
    # Add other formats here as they are implemented
}

def create_video_format_instance(format_name: str):
    """
    Create an instance of the specified video format class.
    
    :param format_name: The name of the video format (e.g., 'quiz', 'wyr').
    :return: An instance of the requested video format class.
    :raises ValueError: If the format name is not supported.
    """
    if format_name not in format_classes:
        raise ValueError(f"Unsupported video format '{format_name}'. Available formats are {list(format_classes.keys())}.")
    
    return format_classes[format_name]()