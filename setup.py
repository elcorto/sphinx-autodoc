import os
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md")) as fd:
    long_description = fd.read()


setup(
    name="sphinx-autodoc",
    version="0.0.0",
    description="almost, but not quite, entirely unlike sphinx-apidoc",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/elcorto/sphinx-autodoc",
    author="Steve Schmerler",
    author_email="git@elcorto.com",
    license="BSD 3-Clause",
    keywords="",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    entry_points={
        "console_scripts": [
            "sphinx-autodoc=sphinx_autodoc.main:main",
        ],
    },
)
