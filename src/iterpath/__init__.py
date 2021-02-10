"""
Iterate through a file tree

Visit <https://github.com/jwodder/iterpath> for more information.
"""

__version__      = '0.1.0.dev1'
__author__       = 'John Thorvald Wodder II'
__author_email__ = 'iterpath@varonathe.org'
__license__      = 'MIT'
__url__          = 'https://github.com/jwodder/iterpath'

from   operator import attrgetter
import os
from   pathlib  import Path
from   typing   import Iterator, NamedTuple

class DirEntries(NamedTuple):
    dirpath: Path
    entries: Iterator[os.DirEntry]

def iterpath(dirpath, topdown=True, include_root=False, dirs=True, sort=False):
    def get_entries(p):
        entries = os.scandir(p)
        if sort:
            entries = iter(sorted(entries, key=attrgetter("name")))
        return DirEntries(Path(p), entries)
    dirstack = [get_entries(dirpath)]
    while dirstack:
        try:
            e = next(dirstack[-1].entries)
        except StopIteration:
            if dirs and not topdown and (len(dirstack) > 1 or include_root):
                yield dirstack[-1].dirpath
            dirstack.pop()
            continue
        if e.is_dir():
            if dirs and topdown and (len(dirstack) > 1 or include_root):
                yield Path(e)
            dirstack.append(get_entries(e))
        else:
            yield Path(e)
