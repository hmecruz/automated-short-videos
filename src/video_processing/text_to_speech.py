import tempfile
import edge_tts
import os
from io import BytesIO


from utils.utils import load_json


class TextToSpeech:
    """
    A class to handle text-to-speech (TTS) operations using a specified configuration.

    This class provides methods to convert text to speech and retrieve voice settings
    based on the language code. It supports saving the generated speech to a memory
    stream or a file.
    """

    def __init__(self, config_path: str = "../config/config.json"):
        """
        Initializes the TextToSpeech instance with the specified configuration path.

        Loads the TTS configuration from the JSON file located at `config_path`.

        :param config_path: str
            The path to the configuration file in JSON format. Defaults to "../config/config.json".
        """
        self.config_path = config_path
        self.config = load_json(self.config_path)

    def get_voice(self, language_code: str) -> str:
        """
        Retrieve the voice setting for a given language code.

        This method looks up the voice setting in the configuration based on the 
        provided language code. If no voice setting is found, it raises a 
        `ValueError`.

        :param language_code: str
            The language code for which to retrieve the voice setting.

        :return: str
            The voice setting corresponding to the provided language code.

        :raises ValueError:
            If no voice setting is found for the provided language code.
        """
        voice = self.config.get("voices", {}).get(language_code, None)

        if voice is None:
            raise ValueError(f"No voice setting found for language code '{language_code}'.")
        return voice

    async def tts_to_memory(self, text: str, language_code: str) -> BytesIO:
        """
        Convert text to speech and return the result as a BytesIO stream.

        This method creates a temporary file to store the generated speech and then
        reads the content back into a BytesIO stream for further processing.

        :param text: str
            The text to be converted to speech.

        :param language_code: str
            The language code that specifies which voice to use for TTS.

        :return: BytesIO
            A BytesIO stream containing the audio data of the generated speech.
        """

        voice = self.get_voice(language_code)

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

    async def tts_to_file(self, text: str, language_code: str, output_file: str):
        """
        Convert text to speech and save the result directly to a file.

        :param text: str
            The text to be converted to speech.

        :param language_code: str
            The language code that specifies which voice to use for TTS.

        :param output_file: str
            The path to the file where the generated speech should be saved.
        """
        voice = self.get_voice(language_code)
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)
