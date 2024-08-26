from video_formats.video_format import VideoFormat


class QuizFormat(VideoFormat):
    format_name = "quiz"

    def __init__(self, config_path="../../config/video_format.json"):
        super().__init__(config_path)

    def get_format_config(self, config):
        return config.get(self.format_name, {})
