import asyncio
from collections.abc import Iterable

from pydub import AudioSegment
from utils.audio_utils import *
from utils.exceptions import AudioProcessingError, DurationExceededError
from utils.json_exceptions import JSONConfigurationError
from utils.utils import cleanup_memory_files
from video_processing.text_to_speech import TextToSpeech
from video_formats.video_format import VideoFormat


class Audio:
    def __init__(self, name: str, data, language_code: str, config, export_dirs: list):
        self.text_to_speech = TextToSpeech()
        self.name = name
        self.data = data
        self.language_code = language_code
        self.config = config
        self.export_dirs = export_dirs
        self._get_config(config)
        

    def _get_config(self, config):
        try:
            VideoFormat.validate_fields(config)
            self.intro_duration = config["intro_duration"]
            self.outro_duration = config["outro_duration"]
            self.video_segment_duration = config["video_segment_duration"]
            self.intro_initial_silence = config["intro_initial_silence"]
            self.outro_initial_silence = config["outro_initial_silence"]
            self.video_segment_initial_silence = config["video_segment_initial_silence"]
        except (KeyError, JSONConfigurationError) as e:
            raise JSONConfigurationError(f"Missing required config key: {str(e)}")

    async def process_audio(self):

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

    async def _generate_audio_segments(self, language_code):

        tasks = [
            asyncio.create_task(self._generate_tts_task(line, language_code))
            for text in self.data.values()
            for line in text
        ]

        # Run all tasks concurrently and wait for them to finish
        audio_segments = await asyncio.gather(*tasks)

        # Map the generated audio segments to intro, content, and outro
        return self._map_audio_segments(audio_segments)

    async def _generate_tts_task(self, text, language_code):
        return await self.text_to_speech.tts_to_memory(text, language_code)

    def _map_audio_segments(self, audio_segments):
        """Map the audio segments to intro, content, and outro based on config."""
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

    def _process_audio_segments(self, audio_segments_map):
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

    def _process_audio_segment(self, audio_segments, segment_type, exceeds_duration=0):

        if isinstance(audio_segments, str):
            audio_segments = [audio_segments]
        elif not isinstance(audio_segments, list):
            raise TypeError(
                f"Expected audio_segments to be a list or string, but got {type(audio_segments)}"
            )

        processed_segments = []

        initial_silence, duration = {
            "intro": (self.intro_initial_silence, self.intro_duration),
            "outro": (self.outro_initial_silence, self.outro_duration),
        }.get(
            segment_type,
            (self.video_segment_initial_silence, self.video_segment_duration),
        )

        for audio_stream in audio_segments:
            try:
                audio = AudioSegment.from_file(audio_stream, format="mp3")
                audio = add_initial_silence(audio, initial_silence)
                audio, exceeds_duration = ensure_required_duration(
                    audio, duration, exceeds_duration
                )
                processed_segments.append(audio)
            except Exception as e:
                raise AudioProcessingError(
                    f"Error processing {segment_type} segment: {str(e)}"
                )

        return processed_segments, exceeds_duration

    def _validate_audio(self, final_audio, processed_segments):
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
                    f"Final audio {self.name} with {final_audio_duration}ms exceeds the expected duration {expected_duration}ms."
                )
            )

        segment_durations = {
            "intro": self.intro_duration,
            "content": self.video_segment_duration,
            "outro": self.outro_duration,
        }

        for segment, duration in zip(
            processed_segments,
            [segment_durations["intro"]]
            + [segment_durations["content"]] * (len(processed_segments) - 2)
            + [segment_durations["outro"]],
        ):
            if len(segment) > duration:
                exceptions.append(
                    DurationExceededError(
                        f"Segment duration ({len(segment)} ms) exceeds the expected duration ({duration} ms) for segment."
                    )
                )

        cleanup_memory_files([final_audio, processed_segments])

        if exceptions:
            raise DurationExceededError(
                "\n".join(str(exception) for exception in exceptions)
            )

        print(f"Final duration: {final_audio_duration} ms")
