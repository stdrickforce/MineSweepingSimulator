# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

try:
    long_description = open("README.rst").read()
except IOError:
    long_description = ""

entry_points = {
    'console_scripts': [
        'sweep = vskfz.main:simulate'
    ],
}

setup(
    name="MineSweepingSimulator",
    version="0.1.0",
    description="A python mine sweeping simulator",
    license="MIT",
    author="stdrickforce",
    entry_points=entry_points,
    packages=find_packages(),
    install_requires=[],
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ]
)
