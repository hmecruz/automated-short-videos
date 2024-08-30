from video_formats.video_format import VideoFormat

class QuizFormat(VideoFormat):
    """
    A class representing the 'quiz' video format.

    This class is a specific implementation of the VideoFormat base class, 
    designed to handle configurations and processing for quiz-style videos.
    """

    format_name = "quiz"

    def __init__(self):
        """
        Initializes the QuizFormat instance by calling the parent VideoFormat class initializer.
        """
        super().__init__()
        