import asyncio
from video_formats import create_video_format_instance
from video_processing.audio_processor import Audio
from utils.utils import load_json
from utils.config_data_utils import get_export_dirs, load_data_files
from utils.exceptions import DurationExceededError

async def main():
    
    config = load_json("../config/config.json")
    export_dirs = get_export_dirs(config)
    data_file_paths = config.get("data_file_paths", [])
    data = load_data_files(data_file_paths)
    
    video_format_instances = {}

    for video in data:
        try:
            video_name = video["name"]
            video_format_name = video["format"]
            content = video["content"]
            
            # Create or reuse the video format instance
            if video_format_name not in video_format_instances:
                video_format_instances[video_format_name] = create_video_format_instance(video_format_name)

            video_format = video_format_instances[video_format_name] 
            format_config = video_format.get_config()
        except Exception as e:
            print(f"Skipping audio processing {f"'{video_name}' " if video_name else None}for due to an error: {e}")
            continue # Skip this cycle if retrieving info goes wrong 

        # Process audio for each language in content
        for language_code, language_content in content.items():
            try:
                audio_name = f"{video_name}"
                audio_data = {
                    "intro": language_content.get("intro", ""),
                    "content": language_content.get("content", []),
                    "outro": language_content.get("outro", "")
                }

                audio_processor = Audio(audio_name, audio_data, language_code, format_config, export_dirs["audio"])
                await audio_processor.process_audio()  
            except DurationExceededError as e:
                print(f"Warning: {e}")
            except Exception as e:
                print(f"Skipping audio processing for '{audio_name} {language_code}' due to an error: {e}")
                

    print("Processing completed.")
    
if __name__ == "__main__":
    asyncio.run(main())
