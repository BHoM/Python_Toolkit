from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")
requirements = [i.strip() for i in (here / "requirements.txt").read_text(encoding="utf-8-sig").splitlines()]

setup(
    name="python_toolkit",
    version="0.0.0",
    description="A Python library that enables Python to be used within BHoM workflows",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BHoM/Python_Toolkit",
    author="BHoM",
    author_email="bhombot@burohappold.com",
    package_dir={"": "src"},
    packages=find_packages(where="src", exclude=['tests']),
    include_package_data=True,
    python_requires=">=3.10, <4",
    install_requires=requirements,
    # If there are data files included in your packages that need to be
    # installed, specify them here.
    package_data={},
)
