import setuptools
import os

# fuck distutils2
version_file = os.path.join('timetools', 'version.txt')
with open(version_file, "r") as fh:
    __version__ = fh.read().rstrip('\n')

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
    install_requires=[
        'numpy', 'matplotlib',
        # === optional requirements
        # 'obspy', 'pytest',  # used for testing
        # 'ipython'
        ],
    scripts=["timetools/bin/doy"])
