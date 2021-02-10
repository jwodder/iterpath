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
from   typing   import Iterator, NamedTuple, Union

class DirEntries(NamedTuple):
    dirpath: Path
    entries: Iterator[os.DirEntry]

def iterpath(
    dirpath: Union[str, os.PathLike],
    topdown: bool = True,
    include_root: bool = False,
    dirs: bool = True,
    sort: bool = False,
) -> Iterator[Path]:

    def get_entries(p: Union[str, os.PathLike]) -> DirEntries:
        entries: Iterator[os.DirEntry] = os.scandir(p)
        if sort:
            entries = iter(sorted(entries, key=attrgetter("name")))
        return DirEntries(Path(p), entries)

    dirstack = [get_entries(dirpath)]
    if include_root and topdown:
        yield dirstack[0].dirpath
    while dirstack:
        try:
            e = next(dirstack[-1].entries)
        except StopIteration:
            d = dirstack.pop()
            if dirs and not topdown and (dirstack or include_root):
                yield d.dirpath
            continue
        if e.is_dir():
            if dirs and topdown:
                yield Path(e)
            dirstack.append(get_entries(e))
        else:
            yield Path(e)
