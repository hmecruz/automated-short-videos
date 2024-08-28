import io
import json
import os

import edge_tts

from utils.json_exceptions import JSONConfigurationError, JSONWarning


class TextToSpeech:

    def __init__(self, config_path="../../config/config.json"):
        self.config_path = config_path
        self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(
                f"Configuration file not found at {self.config_path}"
            )

        try:
            with open(self.config_path, "r") as file:
                self.config = json.load(file)
        except json.JSONDecodeError as e:
            raise JSONConfigurationError(
                f"Error parsing the configuration file: {str(e)}"
            )

    def get_voice(self, language_code):
        """Retrieve the voice setting for a given language code."""
        return self.config.get("voices", {}).get(language_code, None)

    async def tts_to_memory(self, text, language_code):
        voice = self.get_voice(language_code)
        if not voice:
            raise ValueError(f"No voice found for language code {language_code}")

        audio_stream = io.BytesIO()

        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(audio_stream)

        audio_stream.seek(
            0
        )  # Rewind the stream to the beginning so it can be read from the start

        return audio_stream

    async def tts_to_file(self, text, language_code, output_file):
        voice = self.get_voice(language_code)
        if not voice:
            raise ValueError(f"No voice found for language code {language_code}")

        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)
