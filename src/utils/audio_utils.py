import os

from pydub import AudioSegment


def add_initial_silence(audio: AudioSegment, silence_duration: int) -> AudioSegment:
    """
    Add a specified duration of silence to the beginning of an audio segment.

    :param audio: AudioSegment
        The original audio segment to which silence will be added.
    :param silence_duration: int
        The duration of the silence in milliseconds to add at the beginning.
    :return: AudioSegment
        The audio segment with the added initial silence.
    """
    silence_segment = AudioSegment.silent(duration=silence_duration)
    return silence_segment + audio


def ensure_required_duration(audio: AudioSegment, required_duration: int, exceeds_duration: int = 0) -> tuple[AudioSegment, int]:
    """
    Adjust the audio segment to meet a specified duration by adding silence or handling excess duration.

    If the duration of the audio segment is less than the required duration, silence will be added to 
    reach the required length. If the previous segment's duration exceeds the required duration, the 
    additional duration from the previous segment will be accounted for when adding silence.

    If the audio segment exceeds the required duration, it will be returned as is, and the excess 
    duration will be updated accordingly.

    :param audio: AudioSegment
        The audio segment to be adjusted.
    :param required_duration: int
        The target duration for the audio segment in milliseconds.
    :param exceeds_duration: int, optional
        The excess duration from a previous segment, in milliseconds. This is used to adjust the 
        amount of silence added if the previous segment was too long. Default is 0.
    :return: tuple[AudioSegment, int]
        A tuple where the first element is the adjusted audio segment, and the second element is the 
        updated excess duration after adjusting the segment.
    """
    total_duration = len(audio)
    # Determine the amount of silence needed
    if total_duration < required_duration:
        if not exceeds_duration:
            remaining_silence = AudioSegment.silent(
                duration=required_duration - total_duration
            )
        else:
            remaining_silence = AudioSegment.silent(
                duration=required_duration - (total_duration + exceeds_duration)
            )
        audio += remaining_silence
        exceeds_duration = 0
    elif total_duration > required_duration:
        exceeds_duration = total_duration - required_duration

    return audio, exceeds_duration


def concatenate_audio(audio_segments: list[AudioSegment]) -> AudioSegment: 
    """
    Concatenate a list of audio segments into a single audio segment.

    :param audio_segments: list[AudioSegment]
        A list of audio segments to be concatenated.
    :return: AudioSegment
        A single combined audio segment.
    """
    combined_audio = AudioSegment.empty()
    for audio in audio_segments:
        combined_audio += audio
    return combined_audio


def export_audio(audio: AudioSegment, audio_name: str, language_code: str, export_dirs: list):
    """
    Export the final processed audio to multiple directories.

    :param audio: AudioSegment
        The final audio segment to be exported.
    :param audio_name: str
        The base name of the audio file.
    :param language_code: str
        The language code to be included in the exported file name.
    :param export_dirs: list[str]
        A list of directory paths where the audio file should be exported.
    """
    for dir_path in export_dirs:
        output_path = os.path.join(dir_path, f"{audio_name}_final_{language_code}.wav")
        audio.export(output_path, format="wav")
