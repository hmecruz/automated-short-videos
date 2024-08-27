import os
import json
import asyncio
from video_formats.quiz_format import QuizFormat
from video_formats.wyr_format import WYRFormat
from video_processing.audio_processor import Audio
from utils.json_exceptions import JSONConfigurationError
from utils.config_utils import load_config, get_export_dirs


def load_data_files(data_file_paths):
    if not data_file_paths:
        raise ValueError("No data file paths specified.")
    
    data = []
    
    for path in data_file_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Data file not found at {path}")
        
        with open(path, "r") as file:
            data.extend(json.load(file))
    
    return data

def create_video_format_instance(format_name, config_path):
    format_classes = {
        "quiz": QuizFormat,
        "wyr": WYRFormat
        # Add other formats as they are implemented
    }
    
    if format_name not in format_classes:
        raise ValueError(f"Unsupported video format: {format_name}")
    
    return format_classes[format_name](config_path=config_path)

def main():
    try:
        config = load_config("config/config.json")
        
        export_dirs = get_export_dirs(config)
        data_file_paths = config.get("data_file_paths", [])
        data = load_data_files(data_file_paths)
        
        for entry in data:
            video_name = entry["name"]
            video_format_name = entry["video_format"]
            content = entry["content"]
            
            video_format = create_video_format_instance(video_format_name, "../../config/video_format.json")
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
