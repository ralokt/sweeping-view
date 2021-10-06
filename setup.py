from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="sweeping-view",
    description="Readers for Minesweeper replays",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    author="Thomas Kolar",
    author_email="thomaskolar90@gmail.com",
    url="https://github.com/ralokt/sweeping-view/",
    packages=["sweeping_view"],
    platforms=["all"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Other Audience",
        "Topic :: Games/Entertainment :: Puzzle Games",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    keywords=[
        "minesweeper",
        "replay",
        "readers",
    ],
)
