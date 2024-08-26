import video_processing.audio_processor as Audio
import video_processing.image_processor as Image


class Video:
    def __init__(
        self, name, image: Image.Image, audio: Audio.Audio, format: "VideoFormat"
    ):
        self.name = name
        self.image = image
        self.audio = audio
        self.format = format

    def combine(self):
        # Here you can implement logic to combine image and audio into a final video output.
        pass

    def process(self):
        # Example process method that could be expanded:
        self.audio.process_audio(self.format)
