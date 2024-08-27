import os
import json
import asyncio
from video_formats import create_video_format_instance
from video_formats.quiz_format import QuizFormat
from video_formats.wyr_format import WYRFormat
from video_processing.audio_processor import Audio
from utils.json_exceptions import JSONConfigurationError
from utils.utils import load_json
from utils.config_data_utils import get_export_dirs, load_data_files


def main():
    try:
        config = load_json("config/config.json")
        
        export_dirs = get_export_dirs(config)
        data_file_paths = config.get("data_file_paths", [])
        
        data = load_data_files(data_file_paths)
        
        for video in data:
            video_name = video["name"]
            video_format_name = video["format"]
            content = video["content"]
            
            video_format = create_video_format_instance(video_format_name)
            format_config = video_format.get_config()
            
            # Process audio for each language in content
            for language_code, language_content in content.items():
                audio_name = f"{video_name}_{language_code}"
                audio_data = {
                    "intro": language_content.get("intro", ""),
                    "content": language_content.get("content", []),
                    "outro": language_content.get("outro", "")
                }
                
                audio_processor = Audio(audio_name, audio_data, format_config, export_dirs)
                asyncio.run(audio_processor.process_audio(export_dirs["audio"], language_code, export_dirs))
        
        print("Processing completed successfully.")
    
    except (FileNotFoundError, JSONConfigurationError, ValueError) as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
