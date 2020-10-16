import setuptools


with open("Readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="timetools", # Replace with your own username
    version="0.1",
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
