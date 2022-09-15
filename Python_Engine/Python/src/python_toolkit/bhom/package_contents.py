import importlib.util
from pathlib import Path
import os

MODULE_EXTENSIONS = '.py'

def package_contents(package_name, exclude = None):
    """Recursively traverse a module to find all packages within, and return these as a list of strings"""

    spec = importlib.util.find_spec(package_name)
    if spec is None:
        return set()

    pathname = Path(spec.origin).parent
    ret = set()
    with os.scandir(pathname) as entries:
        for entry in entries:
            if entry.name.startswith('__'):
                continue
            current = '.'.join((package_name, entry.name.partition('.')[0]))
            if entry.is_file():
                if exclude is not None:
                    for x in exclude:
                        if x in entry.name:
                            continue
                if entry.name.endswith(MODULE_EXTENSIONS):
                    ret.add(current)
            elif entry.is_dir():
                ret.add(current)
                ret |= package_contents(current)

    return ret
