import os

from pydub import AudioSegment


def add_initial_silence(audio, silence_duration):
    silence_segment = AudioSegment.silent(duration=silence_duration)
    return silence_segment + audio


def ensure_required_duration(audio, required_duration, exceeds_duration=0):
    total_duration = len(audio)
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


def concatenate_audio(audio_segments):
    combined_audio = AudioSegment.empty()
    for audio in audio_segments:
        combined_audio += audio
    return combined_audio


def export_audio(audio, audio_name: str, language_code: str, export_dirs: list):
    for dir_path in export_dirs:
        print(dir_path)
        print(audio_name)
        output_path = os.path.join(dir_path, f"{audio_name}_final_{language_code}.mp3")
        audio.export(output_path, format="mp3")
