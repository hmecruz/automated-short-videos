import gc


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
