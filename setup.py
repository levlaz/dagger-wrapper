import os
import sys

from setuptools import setup
from setuptools.command.install import install

setup(
    name="dagger-wrapper",
    version="0.0.1",
    description="Example of Wrapping Dagger SDK",
    url="https://github.com/levlaz/dagger-wrapper",
    author="Lev Lazinskiy",
    author_email="lev@levlaz.org",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="dagger ci cd sdk",
    packages=["daggerwrapper"],
    install_requires=["dagger-io"],
    python_requires=">=3"
)
