"""
Iterate through a file tree

``iterpath`` lets you iterate over a file tree as a single iterator of
`pathlib.Path` objects, eliminating the need to combine lists returned by
`os.walk()` or recursively call `Path.iterdir()` or `os.scandir()`.  Besides
the standard `os.walk()` options, the library also includes options for sorting
& filtering entries.

Visit <https://github.com/jwodder/iterpath> for more information.
"""

__version__ = "0.4.0"
__author__ = "John Thorvald Wodder II"
__author_email__ = "iterpath@varonathe.org"
__license__ = "MIT"
__url__ = "https://github.com/jwodder/iterpath"

__all__ = [
    "Iterpath",
    "SELECT_DOTS",
    "SELECT_VCS",
    "SELECT_VCS_DIRS",
    "SELECT_VCS_FILES",
    "SelectAny",
    "SelectGlob",
    "SelectNames",
    "SelectRegex",
    "Selector",
    "iterpath",
]

from .core import Iterpath, iterpath
from .selectors import (
    SELECT_DOTS,
    SELECT_VCS,
    SELECT_VCS_DIRS,
    SELECT_VCS_FILES,
    SelectAny,
    SelectGlob,
    SelectNames,
    Selector,
    SelectRegex,
)
