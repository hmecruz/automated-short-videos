from video_formats.video_format import VideoFormat


class QuizFormat(VideoFormat):
    format_name = "quiz"

    def __init__(self):
        super().__init__()

    def get_format_config(self, config):
        return config.get(self.format_name, {})
