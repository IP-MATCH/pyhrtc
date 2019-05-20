import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyhrtc",
    version="0.0.2",
    author="William Pettersson",
    author_email="william@ewpettersson.se",
    description="Various algorithms and utilities for stable matching problems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IP-MATCH/pyhrtc",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
    ],
)
