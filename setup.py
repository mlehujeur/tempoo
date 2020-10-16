import setuptools
from timetools.version import __version__


with open("Readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="timetools", # Replace with your own username
    version=__version__,
    author="Maximilien Lehujeur",
    author_email="maximilien.lehujeur@gmail.com",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    scripts=["timetools/bin/doy"])
