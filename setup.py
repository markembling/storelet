import os
import re
from setuptools import setup

def read_file(filename):
    """Load the contents of the given file (relative to setup.py)"""
    with open(os.path.join(os.path.dirname(__file__), filename)) as file:
        return file.read()

def get_metadata():
    """Parse out all metadata from the module without importing it"""
    py_src = read_file("storelet.py")
    meta = dict(re.findall("__([a-z]+)__ = [\"'](.+)[\"']", py_src))
    return meta

meta = get_metadata()
setup(
    name="storelet",
    version=meta["version"],
    description="Simple and easy framework for writing backup scripts",
    long_description=read_file("README.rst"),
    author=meta["author"],
    author_email=meta["email"],
    url="http://github.com/markembling/storelet",
    license="BSD",
    py_modules=["storelet"],
    install_requires=["boto"],
    classifiers=[
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: BSD License",
    "Topic :: System :: Archiving :: Backup"
])
