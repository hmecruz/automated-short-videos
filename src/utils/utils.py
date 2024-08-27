import gc
import os
import json
from utils.json_exceptions import JSONConfigurationError


def cleanup_memory_files(files: list):
    def _cleanup(item):
        if isinstance(item, list):
            for sub_item in item:
                _cleanup(sub_item)
        else:
            del item

    for file in files:
        _cleanup(file)

    gc.collect()
    print("Temporary files deleted")



def load_json(file_path):
    """Load JSON configuration from a file.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        dict: Parsed JSON data.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        JSONConfigurationError: If there is an error parsing the JSON file or any other issue occurs.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Configuration file not found at {file_path}")

    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except json.JSONDecodeError as e:
        raise JSONConfigurationError(f"Error decoding JSON from file {file_path}: {str(e)}")
    except Exception as e:
        raise JSONConfigurationError(f"An error occurred while processing the file {file_path}: {str(e)}")

    return data
