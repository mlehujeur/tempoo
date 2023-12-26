import setuptools
import os


version_file = os.path.join('tempoo', 'version.py')
if not os.path.isfile(version_file):
    raise IOError(version_file)

with open(version_file, "r") as fid:
    for line in fid:
        if line.strip('\n').strip().startswith('__version__'):
            __version__ = line.strip('\n').split('=')[-1].split()[0].strip().strip('"').strip("'")
            break
    else:
        raise Exception(f'could not detect __version__ affectation in {version_file}')


with open("Readme.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="tempoo", 
    version=__version__,
    author="Maximilien Lehujeur",
    author_email="maximilien.lehujeur@univ-eiffel.fr",
    license="MIT",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        ],
    python_requires='>=3.7, <3.11',
    install_requires=[
        'numpy', 'matplotlib', 'pytest', "pytz"],
    scripts=[os.path.join("tempoo", "bin", "doy"),
             os.path.join("tempoo", "timeline.py"),
    ])

