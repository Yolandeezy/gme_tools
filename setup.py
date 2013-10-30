#! /usr/bin/python

from setuptools.command import easy_install
from setuptools import setup, find_packages
import shutil
import os.path
import sys
import hashlib

# Make it possible to overide script wrapping
old_is_python_script = easy_install.is_python_script
def is_python_script(script_text, filename):
    if 'SETUPTOOLS_DO_NOT_WRAP' in script_text:
        return False
    return old_is_python_script(script_text, filename)
easy_install.is_python_script = is_python_script

setup(
    name = "gme_tools",
    description = "Google Mapsengine GeoTIFF uploader script",
    keywords = "gme geotiff",
    install_requires = ["httplib2==0.8", "oauth2client==1.2"],
    version = "0.0.1",
    author = "Egil Moeller",
    author_email = "egil@skytruth.org",
    license = "GPL",
    url = "https://github.com/SkyTruth/gme_tools",
    scripts = ["gme_tools/mapsengineupload.py"]
)
