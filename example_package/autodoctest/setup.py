import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))


setup(
    name="autodoctest",
    version="1.2.3",
    description="",
    url="https://git.focker.com/xyz",
    author="Gaylord Focker",
    author_email="git@focker.com",
    license="BSD 3-Clause",
    keywords="k3y w0rd",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3",
)
