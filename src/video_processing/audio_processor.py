import asyncio
import os

from pydub import AudioSegment
from utils.exceptions import DurationExceededError
from utils.json_exceptions import JSONConfigurationError
from video_processing.text_to_speech import TextToSpeech


class Audio:

    # INTRO_OUTRO_DURATION = 0
    # VIDEO_SEGEMENT_DURATION = 0
    # INITIAL_SILENCE_INTRO_OUTRO = 0
    # INITIAL_SILENCE_VIDEO_SEGMENT = 0

    def __init__(self, include_intro_outro):
        self.text_to_speech = TextToSpeech()
        self.include_intro_outro = include_intro_outro

    async def process_video(
        self, video_name, lines, language, video_path, export_dirs=None
    ):
        tasks = []
        temp_files = []  # To keep track of generated temporary files
        for i, line in enumerate(lines):
            text = line.strip()
            if text:
                tasks.append(
                    asyncio.create_task(
                        self._generate_tts_task(
                            video_name, i + 1, text, video_path, language
                        )
                    )
                )

        if self.include_intro_outro:
            outro_text = "Like and subscribe or don't, Who cares!"
            tasks.append(
                asyncio.create_task(
                    self._generate_tts_task(
                        video_name,
                        len(tasks) + 1,
                        outro_text,
                        video_path,
                        language="en",
                    )
                )
            )  # Always English

        if tasks:
            audio_segments = await asyncio.gather(*tasks)
            print("All TTS tasks completed successfully!")

            # Extract temporary file paths
            temp_files = [output_file for index, output_file in audio_segments]

            processed_segments, temp_files_exceed_duration = (
                self._process_audio_segments(audio_segments)
            )
            final_audio = self._concatenate_audio(processed_segments)
            export_dirs = export_dirs if export_dirs else []
            export_dirs.append(video_path)
            self._export_final_audio(final_audio, video_name, language, export_dirs)
            self._validate_and_cleanup(
                final_audio, processed_segments, temp_files, temp_files_exceed_duration
            )

        else:
            print("No valid lines found in the input file.")
            raise ValueError("No valid lines found in the input file.")

    async def _generate_tts_task(self, video_name, index, text, video_path, language):
        output_file = os.path.join(video_path, f"{video_name}_{index}_{language}.mp3")
        await self.text_to_speech.tts(text, output_file, language)
        return index, output_file

    def _process_audio_segments(self, audio_segments):
        processed_segments = []
        exceeds_duration = False
        exceeds_delay = 0
        temp_files_exceed_duration = False
        for index, output_file in audio_segments:
            audio = AudioSegment.from_file(output_file, format="mp3")

            # Determine if the current segment is intro/outro or a question
            if self.include_intro_outro and (
                index == 1 or index == len(audio_segments)
            ):
                initial_silence = self.INITIAL_SILENCE_INTRO_OUTRO
                required_audio_duration = self.INTRO_OUTRO_DURATION
            else:
                initial_silence = self.INITIAL_SILENCE_VIDEO_SEGMENT
                required_audio_duration = self.VIDEO_SEGEMENT_DURATION

            audio = self._add_initial_silence(audio, initial_silence)
            audio, exceeds_duration, exceeds_delay = self._ensure_required_duration(
                audio, required_audio_duration, exceeds_duration, exceeds_delay
            )
            if exceeds_duration:
                temp_files_exceed_duration = True
            processed_segments.append(audio)
            print(f"Processed segment {index} with silence added.")
            print(f"Audio duration: {len(audio)} ms")

        return processed_segments, temp_files_exceed_duration

    def _add_initial_silence(self, audio, initial_silence):
        silence_segment = AudioSegment.silent(duration=initial_silence)
        return silence_segment + audio

    def _ensure_required_duration(
        self, audio, required_audio_duration, exceeds_duration, exceeds_delay
    ):
        total_duration = len(audio)
        if total_duration < required_audio_duration:
            if not exceeds_duration:
                remaining_silence = AudioSegment.silent(
                    duration=required_audio_duration - total_duration
                )
            else:
                remaining_silence = AudioSegment.silent(
                    duration=required_audio_duration - (total_duration + exceeds_delay)
                )
            audio += remaining_silence
            exceeds_duration = False
            exceeds_delay = 0
        elif total_duration > required_audio_duration:
            exceeds_duration = True
            exceeds_delay = total_duration - required_audio_duration
        return audio, exceeds_duration, exceeds_delay

    def _concatenate_audio(self, processed_segments):
        combined = AudioSegment.empty()
        for audio in processed_segments:
            combined += audio
        return combined

    def _export_final_audio(self, final_audio, video_name, language, export_dirs):
        for dir_path in export_dirs:
            final_output_file = os.path.join(
                dir_path, f"{video_name}_final_{language}.mp3"
            )
            final_audio.export(final_output_file, format="mp3")
            print(f"Final audio file {final_output_file} created.")

    def _validate_and_cleanup(
        self, final_audio, processed_segments, temp_files, temp_files_exceed_duration
    ):
        expected_duration = self.get_expected_duration(len(processed_segments))
        final_duration = len(final_audio)

        if final_duration <= expected_duration:
            if temp_files_exceed_duration:
                temp_files_lengths = [len(audio) for audio in processed_segments]
                self._cleanup_temp_files(temp_files)
                print(f"Final duration: {final_duration} ms")
                raise DurationExceededError(
                    final_duration, expected_duration, temp_files_lengths
                )
            else:
                self._cleanup_temp_files(temp_files)
                print(f"Final duration: {final_duration} ms")
        else:
            temp_files_lengths = [len(audio) for audio in processed_segments]
            self._cleanup_temp_files(temp_files)
            raise DurationExceededError(
                final_duration, expected_duration, temp_files_lengths
            )

    def _cleanup_temp_files(self, temp_files):
        for file_path in temp_files:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Temporary file {file_path} deleted.")

    def get_intro_outro_duration(self):
        """This method should be overridden by subclasses"""
        """Return the required duration for intro/outro segments."""
        raise NotImplementedError

    def get_video_segment_duration(self):
        """This method should be overridden by subclasses"""
        """Return the required duration for video segments."""
        raise NotImplementedError

    def get_initial_silence_intro_outro(self):
        """This method should be overridden by subclasses"""
        """Return the initial silence duration for intro/outro segments."""
        raise NotImplementedError

    def get_initial_silence_video_segment(self):
        """This method should be overridden by subclasses"""
        """Return the initial silence duration for video segments."""
        raise NotImplementedError

    def get_expected_duration(self, num_segments):
        """This method should be overridden by subclasses"""
        """Calculate the expected final audio duration based on the number of segments."""
        raise NotImplementedError
