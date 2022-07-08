from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")
requirements = [i.strip() for i in (here / "requirements.txt").read_text(encoding="utf-8-sig").splitlines()]

# TODO - populate values here with values from global config instead
setup(
    name="python_toolkit",
    author="BHoM",
    author_email="bhombot@burohappold.com",
    description="A Python library that enables Python to be used within BHoM workflows",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BHoM/Python_Toolkit",
    package_dir={"": "src"},
    packages=find_packages(where="src", exclude=['tests']),
    install_requires=requirements,
)
