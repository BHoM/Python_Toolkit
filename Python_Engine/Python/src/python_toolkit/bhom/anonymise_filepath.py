from pathlib import Path

def anonymise_filepath(filepath):
    """Remove user identifying information from a filepath
    NOTE: This currently only removes <USERNAME> from after "Users".
    """

    fp = Path(filepath)
    file_parts = list(fp.parts)

    username_index = None
    for n, part in enumerate(file_parts):
        if part.lower() == "users":
            username_index = n + 1

    if username_index is None:
        return fp.as_posix()

    file_parts[username_index] = "<USERNAME>"

    return Path(*file_parts).as_posix()
