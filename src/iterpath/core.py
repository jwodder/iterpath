from __future__ import annotations
from collections import deque
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from operator import attrgetter
import os
from pathlib import Path
import sys
from types import TracebackType
from typing import TYPE_CHECKING, Any, AnyStr, Generic, Optional, TypeVar, Union, cast

if TYPE_CHECKING:
    if sys.version_info[:2] >= (3, 8):
        from typing import Protocol
    else:
        from typing_extensions import Protocol

    T_contra = TypeVar("T_contra", contravariant=True)

    class SupportsLT(Protocol[T_contra]):
        def __lt__(self, other: T_contra) -> bool:
            ...

    class SupportsGT(Protocol[T_contra]):
        def __gt__(self, other: T_contra) -> bool:
            ...

    SupportsRichComparison = Union[SupportsLT[Any], SupportsGT[Any]]

    class ScandirIterator(Protocol[AnyStr], Iterator[os.DirEntry[AnyStr]]):
        def close(self) -> None:
            ...

    class DirEntryIter(Protocol[AnyStr], Iterator[os.DirEntry[AnyStr]]):
        dirpath: Path

        def close(self) -> None:
            ...


@dataclass
class FilteredDirEntries(Generic[AnyStr]):
    dirpath: Path
    scaniter: ScandirIterator[AnyStr]
    iterpath: Iterpath[AnyStr]

    def __iter__(self) -> FilteredDirEntries:
        return self

    def __next__(self) -> os.DirEntry[AnyStr]:
        while True:
            e = next(self.scaniter)
            if self.iterpath.filter_entry(e):
                return e

    def close(self) -> None:
        self.scaniter.close()


@dataclass
class SortedDirEntries(Generic[AnyStr]):
    dirpath: Path
    entries: deque[os.DirEntry[AnyStr]]

    def __iter__(self) -> SortedDirEntries:
        return self

    def __next__(self) -> os.DirEntry[AnyStr]:
        try:
            return self.entries.popleft()
        except IndexError:
            raise StopIteration

    def close(self) -> None:
        self.entries.clear()


@dataclass(repr=False, eq=False)
class Iterpath(Generic[AnyStr]):
    """
    The return type of `iterpath()`.  This is both an iterator and a context
    manager.  As an iterator, it traverses a directory tree and yields
    `pathlib.Path` objects.  As a context manager, it returns itself on entry
    and, on exit, closes any remaining internal `os.scandir()` iterators.

    As an alternative to using an `Iterpath` as a context manager, the
    `close()` method can be called explicitly to clean up when finished.

    All other attributes & functionality of this class should be considered
    private.
    """

    dirpath: AnyStr | os.PathLike[AnyStr]
    pdirpath: Path
    filter_dirs: Callable[[os.DirEntry[AnyStr]], Any]
    filter_files: Callable[[os.DirEntry[AnyStr]], Any]
    exclude_dirs: Callable[[os.DirEntry[AnyStr]], Any]
    exclude_files: Callable[[os.DirEntry[AnyStr]], Any]
    topdown: bool
    include_root: bool
    dirs: bool
    sort: bool
    sort_key: Callable[[os.DirEntry[AnyStr]], SupportsRichComparison]
    sort_reverse: bool
    onerror: Optional[Callable[[OSError], Any]]
    followlinks: bool
    return_relative: bool
    dirstack: Optional[list[DirEntryIter[AnyStr]]] = None
    pending: Optional[os.DirEntry[AnyStr]] = None

    def __enter__(self) -> Iterpath:
        return self

    def __exit__(
        self,
        _exc_type: Optional[type[BaseException]],
        _exc_val: Optional[BaseException],
        _exc_tb: Optional[TracebackType],
    ) -> None:
        self.close()

    def __iter__(self) -> Iterpath:
        return self

    def __next__(self) -> Path:
        if self.dirstack is None:
            self.dirstack = [self.get_entries(self.dirpath)]
            if self.include_root and self.topdown:
                return self.relativize(self.dirstack[0].dirpath)
        if self.pending is not None:
            self.dirstack.append(self.get_entries(self.pending))
            self.pending = None
        while self.dirstack:
            try:
                e = next(self.dirstack[-1])
            except (OSError, StopIteration) as exc:
                if isinstance(exc, OSError) and self.onerror is not None:
                    self.onerror(exc)
                d = self.dirstack.pop()
                if (
                    self.dirs
                    and not self.topdown
                    and (self.dirstack or self.include_root)
                ):
                    return self.relativize(d.dirpath)
                continue
            if e.is_dir(follow_symlinks=self.followlinks):
                if self.dirs and self.topdown:
                    self.pending = e
                    return self.relativize(Path(os.fsdecode(e)))
                else:
                    self.dirstack.append(self.get_entries(e))
            else:
                return self.relativize(Path(os.fsdecode(e)))
        raise StopIteration

    def close(self) -> None:
        """
        Close any remaining internal `os.scandir()` iterators and clear the
        directory stack.  After calling this method, no further iteration over
        the `Iterpath` will be possible.

        This method has the same effect as ``__exit__``.
        """
        while self.dirstack:
            self.dirstack.pop().close()

    def filter_entry(self, e: os.DirEntry[AnyStr]) -> bool:
        if e.is_dir(follow_symlinks=self.followlinks):
            return bool(self.filter_dirs(e)) and not self.exclude_dirs(e)
        else:
            return bool(self.filter_files(e)) and not self.exclude_files(e)

    def get_entries(self, p: AnyStr | os.PathLike[AnyStr]) -> DirEntryIter[AnyStr]:
        pp = Path(os.fsdecode(p))
        try:
            # Use fspath() here because PyPy on Windows (as of v7.3.3) requires
            # a string:
            scaniter = os.scandir(os.fspath(p))
        except OSError as exc:
            if self.onerror is not None:
                self.onerror(exc)
            return SortedDirEntries(pp, deque())
        filtered = FilteredDirEntries(pp, scaniter, self)
        if self.sort:
            entry_list = []
            while True:
                try:
                    e = next(filtered)
                except StopIteration:
                    break
                except OSError as exc:
                    if self.onerror is not None:
                        self.onerror(exc)
                    break
                else:
                    entry_list.append(e)
            filtered.close()
            entry_list.sort(key=self.sort_key, reverse=self.sort_reverse)
            return SortedDirEntries(pp, deque(entry_list))
        else:
            return filtered

    def relativize(self, p: Path) -> Path:
        if self.return_relative:
            return p.relative_to(self.pdirpath)
        else:
            return p


def iterpath(
    dirpath: AnyStr | os.PathLike[AnyStr] | None = None,
    *,
    topdown: bool = True,
    include_root: bool = False,
    dirs: bool = True,
    sort: bool = False,
    sort_key: Optional[Callable[[os.DirEntry[AnyStr]], SupportsRichComparison]] = None,
    sort_reverse: bool = False,
    filter: Optional[Callable[[os.DirEntry[AnyStr]], Any]] = None,
    filter_dirs: Optional[Callable[[os.DirEntry[AnyStr]], Any]] = None,
    filter_files: Optional[Callable[[os.DirEntry[AnyStr]], Any]] = None,
    exclude: Optional[Callable[[os.DirEntry[AnyStr]], Any]] = None,
    exclude_dirs: Optional[Callable[[os.DirEntry[AnyStr]], Any]] = None,
    exclude_files: Optional[Callable[[os.DirEntry[AnyStr]], Any]] = None,
    onerror: Optional[Callable[[OSError], Any]] = None,
    followlinks: bool = False,
    return_relative: bool = False,
) -> Iterpath[AnyStr]:
    """
    Iterate through the file tree rooted at the directory ``dirpath`` (by
    default, the current directory) in depth-first order, yielding the files &
    directories within as `pathlib.Path` instances.

    The return value is both an iterator and a context manager.  In order to
    ensure that the internal `os.scandir()` iterators are closed properly,
    either call the ``close()`` method when done or else use it as a context
    manager like so::

        with iterpath(...) as ip:
            for path in ip:
                ...

    If ``return_relative`` is true, the generated `Path` objects will be
    relative to ``dirpath``.  If ``return_relative`` is false (the default) and
    ``dirpath`` is an absolute path, the generated `Path` objects will be
    absolute; otherwise, if ``dirpath`` is a relative path, the `Path` objects
    will be relative and will have ``dirpath`` as a prefix.

    Note that, although `iterpath()` yields `pathlib.Path` objects, it operates
    internally on `os.DirEntry` objects, and so any function supplied as the
    ``sort_key`` parameter or as a filter/exclude parameter must accept
    `os.DirEntry` instances.

    .. versionchanged:: 0.2.0
        ``dirpath`` now defaults to the current directory

    .. versionchanged:: 0.3.0
        ``filter`` and ``exclude`` arguments added

    .. versionchanged:: 0.4.0
        - ``return_relative`` argument added
        - Now usable as a context manager

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
    :param bool return_relative:
        If true, the generated paths will be relative to ``dirpath``
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
        pdirpath = Path()
    else:
        pdirpath = Path(os.fsdecode(dirpath))

    if sort_key is None:
        sort_key = attrgetter("name")

    if filter is not None and filter_dirs is not None:
        raise TypeError("filter and filter_dirs are mutually exclusive")
    elif filter is not None:
        filter_dirs = filter
    elif filter_dirs is None:
        filter_dirs = to_true

    if filter is not None and filter_files is not None:
        raise TypeError("filter and filter_files are mutually exclusive")
    elif filter is not None:
        filter_files = filter
    elif filter_files is None:
        filter_files = to_true

    if exclude is not None and exclude_dirs is not None:
        raise TypeError("exclude and exclude_dirs are mutually exclusive")
    elif exclude is not None:
        exclude_dirs = exclude
    elif exclude_dirs is None:
        exclude_dirs = to_false

    if exclude is not None and exclude_files is not None:
        raise TypeError("exclude and exclude_files are mutually exclusive")
    elif exclude is not None:
        exclude_files = exclude
    elif exclude_files is None:
        exclude_files = to_false

    return Iterpath(
        dirpath=dirpath,
        pdirpath=pdirpath,
        filter_dirs=filter_dirs,
        filter_files=filter_files,
        exclude_dirs=exclude_dirs,
        exclude_files=exclude_files,
        topdown=topdown,
        include_root=include_root,
        dirs=dirs,
        sort=sort,
        sort_key=sort_key,
        sort_reverse=sort_reverse,
        onerror=onerror,
        followlinks=followlinks,
        return_relative=return_relative,
    )


def to_true(_: Any) -> bool:
    return True


def to_false(_: Any) -> bool:
    return False
