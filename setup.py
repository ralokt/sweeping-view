from setuptools import setup

setup(
    name="sweeping-view",
    description="Readers for Minesweeper replays",
    long_description_content_type="text/markdown",
    license="MIT",
    author="Thomas Kolar",
    author_email="thomaskolar90@gmail.com",
    url="https://github.com/ralokt/sweeping-view/",
    packages=["sweeping_view"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Other Audience",
        "Topic :: Games/Entertainment :: Puzzle Games",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    keywords=[
        "minesweeper",
        "replay",
        "readers",
    ],
)
