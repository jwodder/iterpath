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
from   typing   import Any, AnyStr, Callable, Generic, Iterator, Optional, \
                            TYPE_CHECKING, Union

if TYPE_CHECKING:
    from _typeshed import SupportsLessThan

class DirEntries(Generic[AnyStr]):
    def __init__(self, dirpath: Path, entries: Iterator["os.DirEntry[AnyStr]"])\
            -> None:
        self.dirpath: Path = dirpath
        self.entries: Iterator["os.DirEntry[AnyStr]"] = entries


def iterpath(
    dirpath: Union[AnyStr, "os.PathLike[AnyStr]"],
    *,
    topdown: bool = True,
    include_root: bool = False,
    dirs: bool = True,
    sort: bool = False,
    sort_key: Optional[Callable[["os.DirEntry[AnyStr]"], "SupportsLessThan"]]
        = None,
    sort_reverse: bool = False,
    filter_dirs: Optional[Callable[["os.DirEntry[AnyStr]"], Any]] = None,
    filter_files: Optional[Callable[["os.DirEntry[AnyStr]"], Any]] = None,
    onerror: Optional[Callable[[OSError], Any]] = None,
    followlinks: bool = False,
) -> Iterator[Path]:
    if sort_key is not None:
        keyfunc = sort_key
    else:
        keyfunc = attrgetter("name")

    def filter_entry(e: "os.DirEntry[AnyStr]") -> bool:
        if e.is_dir(follow_symlinks=followlinks):
            return filter_dirs is None or bool(filter_dirs(e))
        else:
            return filter_files is None or bool(filter_files(e))

    def get_entries(p: Union[AnyStr, "os.PathLike[AnyStr]"]) \
            -> DirEntries[AnyStr]:
        entries: Iterator["os.DirEntry[AnyStr]"]
        try:
            entries = os.scandir(p)
        except OSError as exc:
            if onerror is not None:
                onerror(exc)
            entries = iter([])
        entries = filter(filter_entry, entries)
        if sort:
            entry_list = []
            while True:
                try:
                    e = next(entries)
                except StopIteration:
                    break
                except OSError as exc:
                    if onerror is not None:
                        onerror(exc)
                    break
                else:
                    entry_list.append(e)
            entry_list.sort(key=keyfunc, reverse=sort_reverse)
            entries = iter(entry_list)
        return DirEntries(Path(os.fsdecode(p)), entries)

    dirstack = [get_entries(dirpath)]
    if include_root and topdown:
        yield dirstack[0].dirpath
    while dirstack:
        try:
            e = next(dirstack[-1].entries)
        except (OSError, StopIteration) as exc:
            if isinstance(exc, OSError) and onerror is not None:
                onerror(exc)
            d = dirstack.pop()
            if dirs and not topdown and (dirstack or include_root):
                yield d.dirpath
            continue
        if e.is_dir(follow_symlinks=followlinks):
            if dirs and topdown:
                yield Path(os.fsdecode(e))
            dirstack.append(get_entries(e))
        else:
            yield Path(os.fsdecode(e))
