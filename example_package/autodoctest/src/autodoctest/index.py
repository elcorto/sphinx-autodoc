"""
This module is called "index.py" and it defines a function "index()".
sphinx-autodoc has no problem with this, while sphinx-apidoc will get
confused, since now there are two files "index.rst", one the index file holding
the TOC, and the file representing this module.
"""

def index(foo):
    pass
