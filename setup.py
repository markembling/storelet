import os
from setuptools import setup
from storelet import __version__

def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as file:
        return file.read()

setup(name="storelet",
      version=__version__,
      description="Simple and easy framework for writing backup scripts",
      long_description=read_file("README.rst"),
      author="Mark Embling",
      author_email="contact@markembling.info",
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
