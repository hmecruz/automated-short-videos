import os

from utils.utils import load_json
from utils.json_exceptions import JSONConfigurationError


def get_export_dirs(config: dict) -> dict:
    """
    Retrieve and validate the export directories from the configuration.

    This function processes the export directory paths specified in the 
    configuration dictionary. Verifies that all required directory types are present, 
    and ensures that the paths are properly formatted and exist.

    :param config: dict
        A dictionary containing configuration settings, including export 
        directories under the keys "export_dirs" and "default_export_dirs".

    :return: dict
        A dictionary mapping export types ("video", "image", "audio") to lists 
        of directory paths.

    :raises JSONConfigurationError:
        If there are unexpected keys, missing required keys, or invalid values 
        in the export dirs and/or default export dirs configuration.
    """
    export_dirs = config.get("export_dirs", {})
    default_dirs = config.get("default_export_dirs", {})

    # Combine and prioritize export_dirs over default_dirs
    export_dirs = {**default_dirs, **export_dirs}

    required_keys = {"video", "image", "audio"}

    # Check for unexpected keys 
    unexpected_export_keys = set(export_dirs) - required_keys
    if unexpected_export_keys:
        raise JSONConfigurationError(f"Unexpected keys in 'export_dirs' / 'default_export_dirs': {', '.join(unexpected_export_keys)}")
    
    # Ensure all required keys are present
    missing_keys = required_keys - export_dirs.keys()
    if missing_keys:
        raise JSONConfigurationError(f"Missing required keys in 'export_dirs' / 'default_export_dirs': {', '.join(missing_keys)}")

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


def load_data_files(data_file_paths: str | list) -> list: 
    """
    Load and aggregate data from multiple JSON files.

    This function takes a list of file paths, loads the JSON data from each 
    file, and combines the data into a single list. If a single file path is 
    provided as a string, it will be converted into a list with one element.

    :param data_file_paths: str | list
        A list of strings representing paths to JSON files, or a single string 
        representing a path to a JSON file.

    :return: list
        A list containing the aggregated data from all the specified JSON files.

    :raises TypeError:
        If `data_file_paths` is not a string or a list of strings.
    """   
    if isinstance(data_file_paths, str):
        data_file_paths = [data_file_paths]
    elif not isinstance(data_file_paths, list) or not all(isinstance(path, str) for path in data_file_paths):
         raise TypeError(
            f"Invalid value for 'data_file_paths': must be a string or a list of "
            "strings representing file paths."
        )

    data = []
    
    for path in data_file_paths:
        file_data = load_json(path)
        data.extend(file_data)
    
    return data
