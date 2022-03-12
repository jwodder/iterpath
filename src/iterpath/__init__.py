"""
Iterate through a file tree

``iterpath`` lets you iterate over a file tree as a single iterator of
``pathlib.Path`` objects, eliminating the need to combine lists returned by
``os.walk()`` or recursively call ``Path.iterdir()`` or ``os.scandir()``.
Besides the standard ``os.walk()`` options, the library also includes options
for sorting & filtering entries.

Visit <https://github.com/jwodder/iterpath> for more information.
"""

__version__ = "0.3.1"
__author__ = "John Thorvald Wodder II"
__author_email__ = "iterpath@varonathe.org"
__license__ = "MIT"
__url__ = "https://github.com/jwodder/iterpath"

from abc import ABC, abstractmethod
import builtins
from dataclasses import dataclass
from fnmatch import fnmatch
from operator import attrgetter
import os
from pathlib import Path
import re
from typing import (
    TYPE_CHECKING,
    Any,
    AnyStr,
    Callable,
    Generic,
    Iterator,
    List,
    Optional,
    Pattern,
    Set,
    Union,
    cast,
)

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison

__all__ = [
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


@dataclass
class DirEntries(Generic[AnyStr]):
    dirpath: Path
    entries: Iterator["os.DirEntry[AnyStr]"]


def iterpath(
    dirpath: Union[AnyStr, "os.PathLike[AnyStr]", None] = None,
    *,
    topdown: bool = True,
    include_root: bool = False,
    dirs: bool = True,
    sort: bool = False,
    sort_key: Optional[
        Callable[["os.DirEntry[AnyStr]"], "SupportsRichComparison"]
    ] = None,
    sort_reverse: bool = False,
    filter: Optional[Callable[["os.DirEntry[AnyStr]"], Any]] = None,
    filter_dirs: Optional[Callable[["os.DirEntry[AnyStr]"], Any]] = None,
    filter_files: Optional[Callable[["os.DirEntry[AnyStr]"], Any]] = None,
    exclude: Optional[Callable[["os.DirEntry[AnyStr]"], Any]] = None,
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

    .. versionchanged:: 0.2.0
        ``dirpath`` now defaults to the current directory

    .. versionchanged:: 0.3.0
        ``filter`` and ``exclude`` arguments added

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
    :param filter:
        Specify a predicate to be applied to all files & directories
        encountered; only those for which the predicate returns a true value
        will be yielded (and, for directories, descended into).

        If ``filter`` is specified, it is an error to also specify
        ``filter_dirs`` or ``filter_files``.
    :param filter_dirs:
        Specify a predicate to be applied to all directories encountered; only
        those for which the predicate returns a true value will be yielded &
        descended into
    :param filter_files:
        Specify a predicate to be applied to all files encountered; only those
        for which the predicate returns a true value will be yielded
    :param exclude:
        Specify a predicate to be applied to all files & directories
        encountered; only those for which the predicate returns a false value
        will be yielded (and, for directories, descended into).

        If ``exclude`` is specified, it is an error to also specify
        ``exclude_dirs`` or ``exclude_files``.
    :param exclude_dirs:
        Specify a predicate to be applied to all directories encountered; only
        those for which the predicate returns a false value will be yielded &
        descended into
    :param exclude_files:
        Specify a predicate to be applied to all files encountered; only those
        for which the predicate returns a false value will be yielded

    If both ``filter`` and ``exclude`` are set, a given entry will only be
    included if ``filter`` returns true and ``exclude`` returns false (that is,
    exclusions take priority over inclusions), and likewise for the directory-
    and file-specific arguments.

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

    if filter is not None and filter_dirs is not None:
        raise TypeError("filter and filter_dirs are mutually exclusive")
    elif filter is not None:
        filter_dirs = filter

    if filter is not None and filter_files is not None:
        raise TypeError("filter and filter_files are mutually exclusive")
    elif filter is not None:
        filter_files = filter

    if exclude is not None and exclude_dirs is not None:
        raise TypeError("exclude and exclude_dirs are mutually exclusive")
    elif exclude is not None:
        exclude_dirs = exclude

    if exclude is not None and exclude_files is not None:
        raise TypeError("exclude and exclude_files are mutually exclusive")
    elif exclude is not None:
        exclude_files = exclude

    def filter_entry(e: "os.DirEntry[AnyStr]") -> bool:
        if e.is_dir(follow_symlinks=followlinks):
            return (filter_dirs is None or bool(filter_dirs(e))) and (
                exclude_dirs is None or not exclude_dirs(e)
            )
        else:
            return (filter_files is None or bool(filter_files(e))) and (
                exclude_files is None or not exclude_files(e)
            )

    def get_entries(p: Union[AnyStr, "os.PathLike[AnyStr]"]) -> DirEntries[AnyStr]:
        entries: Iterator["os.DirEntry[AnyStr]"]
        try:
            # Use fspath() here because PyPy on Windows (as of v7.3.3) requires
            # a string:
            entries = os.scandir(os.fspath(p))
        except OSError as exc:
            if onerror is not None:
                onerror(exc)
            entries = iter([])
        entries = builtins.filter(filter_entry, entries)
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


class Selector(ABC, Generic[AnyStr]):
    """
    .. versionadded:: 0.3.0

    Base class for selectors
    """

    @abstractmethod
    def __call__(self, _entry: "os.DirEntry[AnyStr]") -> bool:
        ...

    def __or__(self, other: "Selector") -> "SelectAny":
        parts: List[Selector] = []
        for s in [self, other]:
            if isinstance(s, SelectAny):
                parts.extend(s.selectors)
            else:
                parts.append(s)
        return SelectAny(parts)


@dataclass
class SelectAny(Selector[AnyStr]):
    """
    .. versionadded:: 0.3.0

    Selects `~os.DirEntry`'s that match any of the given selectors.

    This class is the return type of ``|`` on two selectors.
    """

    selectors: List[Selector[AnyStr]]

    def __call__(self, entry: "os.DirEntry[AnyStr]") -> bool:
        return any(s(entry) for s in self.selectors)


class SelectNames(Selector[AnyStr]):
    """
    .. versionadded:: 0.3.0

    Selects `~os.DirEntry`'s whose names are one of ``names``.  If
    ``case_sensitive`` is `False`, the check is performed case-insensitively.
    """

    def __init__(self, *names: AnyStr, case_sensitive: bool = True) -> None:
        self.names: Set[AnyStr] = set(names)
        self.case_sensitive: bool = case_sensitive
        if not case_sensitive:
            self.names = {n.lower() for n in self.names}

    def __call__(self, entry: "os.DirEntry[AnyStr]") -> bool:
        name = entry.name
        if not self.case_sensitive:
            name = name.lower()
        return name in self.names

    def __repr__(self) -> str:
        return "{}({}, case_sensitive={})".format(
            type(self).__name__,
            ", ".join(map(repr, sorted(self.names))),
            self.case_sensitive,
        )

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, SelectNames):
            return (
                self.names == other.names
                and self.case_sensitive == other.case_sensitive
            )
        else:
            return NotImplemented


@dataclass
class SelectRegex(Selector[AnyStr]):
    """
    .. versionadded:: 0.3.0

    Selects `~os.DirEntry`'s whose names match (using `re.search()`) the given
    regular expression
    """

    pattern: Union[AnyStr, "Pattern[AnyStr]"]

    def __call__(self, entry: "os.DirEntry[AnyStr]") -> bool:
        return bool(re.search(self.pattern, entry.name))


@dataclass
class SelectGlob(Selector[AnyStr]):
    """
    .. versionadded:: 0.3.0

    Selects `~os.DirEntry`'s whose names match the given fileglob pattern
    """

    pattern: AnyStr

    def __call__(self, entry: "os.DirEntry[AnyStr]") -> bool:
        return fnmatch(entry.name, self.pattern)


#: .. versionadded:: 0.3.0
#:
#: Selects `~os.DirEntry`'s whose names begin with a period
SELECT_DOTS = SelectGlob(".*")

#: .. versionadded:: 0.3.0
#:
#: Selects version control directories
SELECT_VCS_DIRS = SelectNames(
    ".git", ".hg", "_darcs", ".bzr", ".svn", "_svn", "CVS", "RCS"
)

#: .. versionadded:: 0.3.0
#:
#: Selects version-control-specific files
SELECT_VCS_FILES = (
    SelectNames(
        ".gitattributes",
        ".gitignore",
        ".gitmodules",
        ".mailmap",
        ".hgignore",
        ".hgsigs",
        ".hgtags",
        ".binaries",
        ".boring",
        ".bzrignore",
    )
    | SelectGlob("?*,v")
)

#: .. versionadded:: 0.3.0
#:
#: Selects `~os.DirEntry`'s matched by either `SELECT_VCS_DIRS` or
#: `SELECT_VCS_FILES`
SELECT_VCS = SELECT_VCS_DIRS | SELECT_VCS_FILES
