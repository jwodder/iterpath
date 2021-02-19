"""
Iterate through a file tree

``iterpath`` lets you iterate over a file tree as a single iterator of
``pathlib.Path`` objects, eliminating the need to combine lists returned by
``os.walk()`` or recursively call ``Path.iterdir()`` or ``os.scandir()``.
Besides the standard ``os.walk()`` options, the library also includes options
for sorting & filtering entries.

Visit <https://github.com/jwodder/iterpath> for more information.
"""

__version__      = '0.2.0'
__author__       = 'John Thorvald Wodder II'
__author_email__ = 'iterpath@varonathe.org'
__license__      = 'MIT'
__url__          = 'https://github.com/jwodder/iterpath'

from   operator import attrgetter
import os
from   pathlib  import Path
from   typing   import Any, AnyStr, Callable, Generic, Iterator, Optional, \
                            TYPE_CHECKING, Union, cast

if TYPE_CHECKING:
    from _typeshed import SupportsLessThan

__all__ = ["iterpath"]

class DirEntries(Generic[AnyStr]):
    def __init__(self, dirpath: Path, entries: Iterator["os.DirEntry[AnyStr]"])\
            -> None:
        self.dirpath: Path = dirpath
        self.entries: Iterator["os.DirEntry[AnyStr]"] = entries


def iterpath(
    dirpath: Union[AnyStr, "os.PathLike[AnyStr]", None] = None,
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
    exclude_dirs: Optional[Callable[["os.DirEntry[AnyStr]"], Any]] = None,
    exclude_files: Optional[Callable[["os.DirEntry[AnyStr]"], Any]] = None,
    onerror: Optional[Callable[[OSError], Any]] = None,
    followlinks: bool = False,
) -> Iterator[Path]:
    """
    Iterate through the file tree rooted at the directory ``dirpath`` (by
    default, the current directory) in depth-first order, yielding the files &
    directories within.  If ``dirpath`` is an absolute path, the generated
    `Path` objects will be absolute; otherwise, if ``dirpath`` is a relative
    path, the `Path` objects will be relative and will have ``dirpath`` as a
    prefix.

    Note that, although `iterpath()` yields `pathlib.Path` objects, it operates
    internally on `os.DirEntry` objects, and so any function supplied as the
    ``sort_key`` parameter or as a filter/exclude parameter must accept
    `os.DirEntry` instances.

    :param dirpath: the directory over which to iterate
    :param bool dirs: Whether to include directories in the output
    :param bool topdown:
        Whether to yield each directory before (`True`) or after (`False`) its
        contents
    :param bool include_root:
        Whether to include the ``dirpath`` argument passed to `iterpath()` in
        the output
    :param bool followlinks:
        Whether to treat a symlink to a directory as a directory
    :param onerror:
        Specify a function to be called whenever an `OSError` is encountered
        while iterating over a directory.  If the function reraises the
        exception, `iterpath()` aborts; otherwise, it continues with the next
        directory.  By default, `OSError` exceptions are ignored.
    :param bool sort:
        Sort the entries in each directory.  When `False`, entries are yielded
        in the order returned by `os.scandir()`.  When `True`, entries are
        sorted, by default, by filename in ascending order, but this can be
        changed via the ``sort_key`` and ``sort_reverse`` arguments.
    :param sort_key:
        Specify a custom key function for sorting directory entries.  Only has
        an effect when ``sort`` is `True`.
    :param bool sort_reverse:
        Sort directory entries in reverse order.  Only has an effect when
        ``sort`` is `True`.
    :param filter_dirs:
        Specify a predicate to be applied to all directories encountered; only
        those for which the predicate returns a true value will be yielded &
        descended into
    :param filter_files:
        Specify a predicate to be applied to all files encountered; only those
        for which the predicate returns a true value will be yielded
    :param exclude_dirs:
        Specify a predicate to be applied to all directories encountered; only
        those for which the predicate returns a false value will be yielded &
        descended into
    :param exclude_files:
        Specify a predicate to be applied to all files encountered; only those
        for which the predicate returns a false value will be yielded

    .. warning::

        If ``dirpath`` is a relative path, changing the working directory while
        `iterpath()` is in progress will lead to errors, or at least inaccurate
        results.

    .. warning::

        Setting ``followlinks`` to `True` can result in infinite recursion if a
        symlink points to a parent directory of itself.
    """

    if dirpath is None:
        dirpath = cast(Union[AnyStr, "os.PathLike[AnyStr]"], os.curdir)

    if sort_key is not None:
        keyfunc = sort_key
    else:
        keyfunc = attrgetter("name")

    def filter_entry(e: "os.DirEntry[AnyStr]") -> bool:
        if e.is_dir(follow_symlinks=followlinks):
            return (
                (filter_dirs is None or bool(filter_dirs(e)))
                and (exclude_dirs is None or not exclude_dirs(e))
            )
        else:
            return (
                (filter_files is None or bool(filter_files(e)))
                and (exclude_files is None or not exclude_files(e))
            )

    def get_entries(p: Union[AnyStr, "os.PathLike[AnyStr]"]) \
            -> DirEntries[AnyStr]:
        entries: Iterator["os.DirEntry[AnyStr]"]
        try:
            # Use fspath() here because PyPy on Windows (as of v7.3.3) requires
            # a string:
            entries = os.scandir(os.fspath(p))
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
