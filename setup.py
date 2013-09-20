#!/usr/bin/env python
# Standard library
from distutils.core import setup
# Project
import iqm

with open('README.rst') as file:
    long_description = file.read()

setup(author="Timid Robot Zehta",
      author_email="tim@clockwork.net",
      classifiers=["Environment :: Console",
                   "License :: OSI Approved :: MIT License",
                   "Topic :: Scientific/Engineering :: Mathematics"],
      description="Interquartile Mean pure-Python module",
      download_url="https://github.com/ClockworkNet/python-iqm/releases",
      license="MIT License",
      long_description=long_description,
      name="python-iqm",
      py_modules=["iqm"],
      url="https://github.com/ClockworkNet/python-iqm",
      version=iqm.VERSION,
      )
