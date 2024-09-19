import asyncio
from io import BytesIO

from pydub import AudioSegment
from utils.audio_utils import *
from utils.exceptions import DurationExceededError
from utils.utils import cleanup_memory_files
from video_processing.text_to_speech import TextToSpeech
from video_formats.video_format import VideoFormat


class Audio:
    """
    A class for processing audio segments and exporting them according to specific video configurations.

    This class handles generating audio from text, processing the audio by adding silences and ensuring 
    required durations, concatenating segments, and exporting the final audio file.
    """
     
    def __init__(self, name: str, data: dict, language_code: str, video_config: dict, export_dirs: list):
        """
        Initializes the Audio class with the necessary attributes.

        :param name: str
            The base name for the final audio file.
        :param data: dict
            The text data to be converted into audio.
        :param language_code: str
            The language code for the text-to-speech conversion.
        :param video_config: dict
            Configuration settings for the video format, including durations and silences.
        :param export_dirs: list[str]
            List of directory paths where the final audio file should be exported.
        """
        self.text_to_speech = TextToSpeech("../config/config.json")
        self.name = name
        self.data = data
        self.language_code = language_code
        self.video_config = video_config
        self.export_dirs = export_dirs
        self._load_video_config(video_config)
        

    def _load_video_config(self, video_config: dict):
        """
        Load and validate video configuration settings.

        This method validates the provided video configuration and initializes
        the relevant attributes such as durations and initial silences. Raises
        an exception if the configuration is missing required keys or is invalid.

        :param video_config: dict
            Configuration settings for video format.
        
        """
        VideoFormat.validate_fields(video_config)
        self.intro_duration = video_config["intro_duration"]
        self.outro_duration = video_config["outro_duration"]
        self.video_segment_duration = video_config["video_segment_duration"]
        self.intro_initial_silence = video_config["intro_initial_silence"]
        self.outro_initial_silence = video_config["outro_initial_silence"]
        self.video_segment_initial_silence = video_config["video_segment_initial_silence"]
        

    async def process_audio(self):
        """
        Process and export audio based on the provided text and video configuration.

        This method generates audio segments from text data, processes each segment by adding silences
        and ensuring the required duration, concatenates all segments into one final audio, and then 
        exports the final audio file. Raises exceptions if any audio processing or validation errors occur.

        """
        # Step 1: Generate temporary audio files from text data
        audio_segments_map = await self._generate_audio_segments(self.language_code)

        # Step 2: Process each audio segment (add silences, ensure duration)
        processed_segments = self._process_audio_segments(audio_segments_map)

        # Step 3: Concatenate all segments into one final audio
        final_audio = concatenate_audio(processed_segments)

        # Step 4: Export the final audio file
        export_audio(final_audio, self.name, self.language_code, self.export_dirs)

        # Validation
        self._validate_audio(final_audio, processed_segments)

    async def _generate_audio_segments(self, language_code: str) -> dict:
        """
        Generate audio segments from the text data using text-to-speech conversion.

        This method creates asynchronous tasks for converting each text entry into audio and maps 
        the generated audio segments to appropriate sections (intro, content, outro).

        :param language_code: str
            The language code for the text-to-speech conversion.

        :return: dict
            A dictionary mapping segment types (intro, content, outro) to the corresponding audio segments.
        """
        tasks = [
            asyncio.create_task(self._generate_tts_task(line, language_code))
            for text in self.data.values()
            for line in (text if isinstance(text, list) else [text])
        ]

        # Run all tasks concurrently and wait for them to finish
        audio_segments = await asyncio.gather(*tasks)

        # Map the generated audio segments to intro, content, and outro
        return self._map_audio_segments(audio_segments)

    async def _generate_tts_task(self, text: str, language_code: str) -> BytesIO:
        """
        Generate a text-to-speech audio segment and return it as a BytesIO stream.

        :param text: str
            The text to be converted into speech.
        :param language_code: str
            The language code for the text-to-speech conversion.

        :return: BytesIO
            The audio segment as a BytesIO stream.
        """
        return await self.text_to_speech.tts_to_memory(text, language_code)

    def _map_audio_segments(self, audio_segments: list[BytesIO]):
        """
        Map the generated audio segments to intro, content, and outro based on video configuration.

        :param audio_segments: list[BytesIO]
            A list of generated audio segments.

        :return: dict
            A dictionary mapping segment types (intro, content, outro) to the corresponding audio segments.
        """
        audio_segments_map = {}

        # Mapping the segments to appropriate sections
        if self.intro_duration > 0:
            audio_segments_map["intro"] = audio_segments[0]
            content_segments = (
                audio_segments[1:-1] if self.outro_duration > 0 else audio_segments[1:]
            )
        else:
            content_segments = (
                audio_segments[:-1] if self.outro_duration > 0 else audio_segments
            )

        audio_segments_map["content"] = content_segments

        if self.outro_duration > 0:
            audio_segments_map["outro"] = audio_segments[-1]

        return audio_segments_map

    def _process_audio_segments(self, audio_segments_map: dict) -> list[AudioSegment]:
        """
        Process audio segments by adding initial silence and ensuring required durations.

        :param audio_segments_map: dict
            A dictionary mapping segment types (intro, content, outro) to the corresponding audio segments.

        :return: list[AudioSegment]
            A list of processed audio segments.
        """
        processed_segments = []
        exceeds_duration = 0

        # Process each segment type
        if "intro" in audio_segments_map:
            intro_segments, exceeds_duration = self._process_audio_segment(
                audio_segments_map["intro"], "intro", exceeds_duration
            )
            processed_segments.extend(intro_segments)

        content_segments, exceeds_duration = self._process_audio_segment(
            audio_segments_map["content"], "content", exceeds_duration
        )
        processed_segments.extend(content_segments)

        if "outro" in audio_segments_map:
            outro_segments, exceeds_duration = self._process_audio_segment(
                audio_segments_map["outro"], "outro", exceeds_duration
            )
            processed_segments.extend(outro_segments)

        return processed_segments

    def _process_audio_segment(self, audio_segments_map: list[BytesIO], segment_type: str, exceeds_duration: int = 0) -> tuple[list[AudioSegment], int]:
        """
        Process an individual audio segment by adding initial silence and ensuring required duration.

        :param audio_segments_map: list[BytesIO]
            A list of audio segments to be processed.
        :param segment_type: str
            The type of the audio segment being processed (intro, content, outro).
        :param exceeds_duration: int
            The accumulated duration exceeding the required length from previous segments.

        :return: tuple[list[AudioSegment], int]
            A tuple where the first element is a list of processed audio segments, and
            the second element is the updated exceeds_duration.
        
        :raises TypeError:
            If `audio_segments_map` is not a list of `BytesIO` instances.

        """
        if isinstance(audio_segments_map, BytesIO):
            audio_segments_map = [audio_segments_map]
        elif not isinstance(audio_segments_map, list) or not all(isinstance(audio_segment, BytesIO) for audio_segment in audio_segments_map):
            raise TypeError(
                f"Expected audio_segments to be a BytesIO or a list of BytesIO, but got {type(audio_segments_map)}"
            )

        processed_segments = []

        initial_silence, duration = {
            "intro": (self.intro_initial_silence, self.intro_duration),
            "outro": (self.outro_initial_silence, self.outro_duration),
        }.get(
            segment_type,
            (self.video_segment_initial_silence, self.video_segment_duration),
        )

        for audio_stream in audio_segments_map:
            audio = AudioSegment.from_file(audio_stream, format="mp3")
            audio = add_initial_silence(audio, initial_silence)
            audio, exceeds_duration = ensure_required_duration(
                audio, duration, exceeds_duration
            )
            processed_segments.append(audio)
            

        return processed_segments, exceeds_duration

    def _validate_audio(self, final_audio: AudioSegment, processed_segments: list[AudioSegment]):
        """
        Validate the final audio and its segments to ensure they meet the expected durations.

        This method checks that the final audio and each segment do not exceed their
        expected durations. If any validation errors occur, they are raised as exceptions.

        :param final_audio: AudioSegment
            The final concatenated audio.
        :param processed_segments: list[AudioSegment]
            The list of processed audio segments.

        :raises DurationExceededError:
            If the final audio or any segment exceeds the expected duration.
        """
        expected_duration = (
            self.intro_duration
            + self.video_segment_duration * (len(processed_segments) - 2)
            + self.outro_duration
        )
        final_audio_duration = len(final_audio)

        exceptions = []

        if final_audio_duration > expected_duration:
            exceptions.append(
                DurationExceededError(
                    f"Final audio '{self.name}_{self.language_code}' duration: {final_audio_duration}ms. Expected duration: {expected_duration}ms."
                )
            )
        else: print(f"Final audio '{self.name}_{self.language_code}' duration: {final_audio_duration}ms.")

        segment_durations = {
            "intro": self.intro_duration,
            "content": self.video_segment_duration,
            "outro": self.outro_duration,
        }

        expected_segment_durations = (
            [segment_durations["intro"]]
            + [segment_durations["content"]] * (len(processed_segments) - 2)
            + [segment_durations["outro"]]
        )

        for segment, expected_duration in zip(processed_segments, expected_segment_durations):
            if len(segment) > expected_duration:
                exceptions.append(
                    DurationExceededError(
                        f"Final audio '{self.name}_{self.language_code}' segments exceed expected durations.\n"
                        f"Segment durations:  {[len(s) for s in processed_segments]}\nExpected durations: {expected_segment_durations}"
                    )
                )
                break

        cleanup_memory_files([final_audio, processed_segments])

        if exceptions:
            raise DurationExceededError(
                "\n".join(str(exception) for exception in exceptions)
            )

