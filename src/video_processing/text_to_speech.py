import tempfile
import edge_tts
import os
from io import BytesIO


from utils.json_exceptions import JSONConfigurationError, JSONWarning
from utils.utils import load_json


class TextToSpeech:

    def __init__(self, config_path="../config/config.json"):
        self.config_path = config_path
        self.config = load_json(self.config_path)

    def get_voice(self, language_code):
        """Retrieve the voice setting for a given language code."""
        return self.config.get("voices", {}).get(language_code, None)

    async def tts_to_memory(self, text, language_code):
        #print(text)
        voice = self.get_voice(language_code)
        if not voice:
            raise ValueError(f"No voice found for language code {language_code}")
        
        # Create a NamedTemporaryFile which can be used as a context manager
        with tempfile.NamedTemporaryFile(delete=False, mode='wb') as temp_file:
            temp_file_path = temp_file.name

        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(temp_file_path)

            # Open the file and return its content as a BytesIO stream
            with open(temp_file_path, 'rb') as file:
                audio_stream = BytesIO(file.read())

            audio_stream.seek(0)  # Rewind the stream to the beginning so it can be read from the start

            return audio_stream
        finally:
            # Clean up the temporary file
            os.remove(temp_file_path)

    async def tts_to_file(self, text, language_code, output_file):
        voice = self.get_voice(language_code)
        if not voice:
            raise ValueError(f"No voice found for language code {language_code}")

        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)
