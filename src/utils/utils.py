import gc
import json


def cleanup_memory_files(files: list):  
    """
    Recursively delete items in a list and trigger garbage collection to free 
    up memory.

    This function takes a list of files or objects and recursively deletes each 
    item, including any nested lists, to ensure that memory is properly freed. 
    After deleting the items, it manually triggers garbage collection to clean 
    up any remaining references.

    :param files: list
        A list containing files or objects to be deleted. The list can include 
        nested lists.
    """
    def _cleanup(item):
        if isinstance(item, list):
            for sub_item in item:
                _cleanup(sub_item)
        else:
            del item

    for file in files:
        _cleanup(file)

    gc.collect()
    

def load_json(file_path: str) -> dict:
    """
    Load and return the contents of a JSON file as a dictionary.

    This function opens the specified JSON file, reads its contents, and parses it into a Python dictionary.

    :param file_path: str
        The path to the JSON file to be loaded.
    :return: dict
        A dictionary containing the parsed JSON data.
    :raises FileNotFoundError: If the specified file does not exist.
    :raises PermissionError: If there is no permission to read the file.
    :raises JSONDecodeError: If the file contains invalid JSON.
    """

    with open(file_path, 'r') as file:
        data = json.load(file)
  
    return data
