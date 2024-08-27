import os
import json
from utils.utils import load_json
from utils.json_exceptions import JSONConfigurationError, JSONFileError


def get_export_dirs(config):
    export_dirs = config.get("export_dirs", {})
    default_dirs = config.get("default_export_dirs", {})

    # Combine and prioritize export_dirs over default_dirs
    export_dirs = {**default_dirs, **export_dirs}

    required_keys = {"video", "image", "audio"}

    # Check for unexpected keys 
    unexpected_export_keys = set(export_dirs) - required_keys
    if unexpected_export_keys:
        raise JSONConfigurationError(f"Unexpected keys in 'export_dirs': {', '.join(unexpected_export_keys)}")
    
    # Ensure all required keys are present
    missing_keys = required_keys - export_dirs.keys()
    if missing_keys:
        raise JSONConfigurationError(f"Missing required keys in 'export_dirs': {', '.join(missing_keys)}")

    for key in export_dirs:
        if isinstance(export_dirs[key], str):
            export_dirs[key] = [export_dirs[key]]
        elif not isinstance(export_dirs, list):
            raise JSONConfigurationError(f"Unexpected value") # Create a better error message indicating the value of the key must be a path or a list of paths
    
    # Validate and normalize paths
    for key, value in export_dirs.items():
        if isinstance(value, str):
            export_dirs[key] = [value]
        elif not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            raise JSONConfigurationError(f"Invalid value for '{key}': must be a string or a list of strings representing directory paths.")

    # Ensure directories exist
    for key, dirs in export_dirs.items():
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
    
    return export_dirs


def load_data_files(data_file_paths):    
    if isinstance(data_file_paths, str):
            data_file_paths = [data_file_paths]
    elif not isinstance(data_file_paths, list):
        raise JSONFileError("Invalid format for 'data_file_paths'. It should be a list of paths or a single path.")

    if not all(isinstance(path, str) for path in data_file_paths):
        raise JSONFileError("All elements in 'data_file_paths' must be strings representing file paths.")

    data = []
    
    for path in data_file_paths:
        file = load_json(path)
        data.extend(json.load(file))
    
    return data
