from video_formats.video_format import VideoFormat

class WYRFormat(VideoFormat):
    """
    A class representing the 'wyr' video format.

    This class is a specific implementation of the VideoFormat base class,
    designed to handle configurations and processing for "Would You Rather"-style videos.
    """

    format_name = "wyr"

    def __init__(self):
        """
        Initializes the WYRFormat instance by calling the parent VideoFormat class initializer.
        """
        super().__init__()
        
