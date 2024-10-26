# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages
import datetime

__version__ = "${VERSION}"
if "$" in __version__:
    __version__ = datetime.datetime.now().strftime("%Y.%m.%d.%H.%M")
print("Version:", __version__)

setup(
    name="beautifulemail",
    version=__version__,
    description="BeautifulEmail is a python package that makes it easy and quick to save pandas dataframes in beautifully formatted excel files. BeautifulEmail is the Openpyxl for Data Scientists with a deadline.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="https://github.com/vanalmsick",
    url="https://github.com/vanalmsick/beautifulemail",
    project_urls={
        "Issues": "https://github.com/vanalmsick/beautifulemail/issues",
        "Documentation": "https://vanalmsick.github.io/beautifulemail/",
        "Source Code": "https://github.com/vanalmsick/beautifulemail",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    #packages=find_packages(),
    install_requires=['markdown2', 'datetime', 'numpy', 'pandas', 'libsass', 'beautifulsoup4'],
    package_data={"beautifulemail": ["templates/*.html", "VERSION"]},
    include_package_data=True,
)
