#!/usr/bin/env python3
"""Setup script for CGC."""

import setuptools

setuptools.setup(
    name="cgc",
    version="1.5.0",
    author="Luke Short",
    author_email="ekultails@gmail.com",
    url="https://github.com/ekultails/card_games_converter",
    description="Card Games Converters. A utility to convert images of" + \
                " cards into a printable format.",
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    packages=["cgc"],
    license="http://www.apache.org/licenses/LICENSE-2.0",
    install_requires=["img2pdf", "Pillow"],
    scripts=["bin/cgc-cli.py"]
)
