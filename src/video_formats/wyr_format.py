from video_formats.video_format import VideoFormat


class WYRFormat(VideoFormat):
    format_name = "wyr"

    def __init__(self):
        super().__init__()

    def get_format_config(self, config):
        return config.get(self.format_name, {})
