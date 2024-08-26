from video_formats.video_format import VideoFormat


class WYRFormat(VideoFormat):
    format_name = "wyr"

    def __init__(self, config_path="../../config/video_format.json"):
        super().__init__(config_path)

    def get_format_config(self, config):
        return config.get(self.format_name, {})
