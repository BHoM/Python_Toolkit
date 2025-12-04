from pathlib import Path
import setuptools

TOOLKIT_NAME = "Python_Toolkit"

here = Path(__file__).parent.resolve()

def _bhom_version() -> str:
    """Return the version of BHoM installed (using the BHoM.dll in the root BHoM directory."""
    versionFile = here / "VERSION.txt" #version file is created in a pre-build event in Python_Engine.csproj
    return versionFile.read_text();

BHOM_VERSION = _bhom_version()

long_description = (here / "README.md").read_text(encoding="utf-8")

setuptools.setup(
    description=f"A Python library that contains minimal code intended to be used by the {TOOLKIT_NAME} Python environment for BHoM workflows.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=BHOM_VERSION,
)
