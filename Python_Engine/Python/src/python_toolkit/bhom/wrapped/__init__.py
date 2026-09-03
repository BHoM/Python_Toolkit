from importlib import import_module
from pathlib import Path
import os

python_files = Path(__file__).parent.glob("**/*.py")

for file in python_files:
    if file.name == "__init__.py":
        continue

    rel = file.relative_to(Path(__file__).parent)
    module = "." + str(rel).replace(".py", "").replace(os.path.sep, ".")
    import_module(module, "python_toolkit.bhom.wrapped")