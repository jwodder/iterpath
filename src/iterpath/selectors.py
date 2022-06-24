from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from fnmatch import fnmatch
import os
import re
from typing import Any, AnyStr, Generic


class Selector(ABC, Generic[AnyStr]):
    """
    .. versionadded:: 0.3.0

    Base class for selectors
    """

    @abstractmethod
    def __call__(self, entry: os.DirEntry[AnyStr]) -> bool:
        ...

    def __or__(self, other: Selector) -> SelectAny:
        parts: list[Selector] = []
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

    selectors: list[Selector[AnyStr]]

    def __call__(self, entry: os.DirEntry[AnyStr]) -> bool:
        return any(s(entry) for s in self.selectors)


class SelectNames(Selector[AnyStr]):
    """
    .. versionadded:: 0.3.0

    Selects `~os.DirEntry`'s whose names are one of ``names``.  If
    ``case_sensitive`` is `False`, the check is performed case-insensitively.
    """

    def __init__(self, *names: AnyStr, case_sensitive: bool = True) -> None:
        self.names: set[AnyStr] = set(names)
        self.case_sensitive: bool = case_sensitive
        if not case_sensitive:
            self.names = {n.lower() for n in self.names}

    def __call__(self, entry: os.DirEntry[AnyStr]) -> bool:
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

    pattern: AnyStr | re.Pattern[AnyStr]

    def __call__(self, entry: os.DirEntry[AnyStr]) -> bool:
        return bool(re.search(self.pattern, entry.name))


@dataclass
class SelectGlob(Selector[AnyStr]):
    """
    .. versionadded:: 0.3.0

    Selects `~os.DirEntry`'s whose names match the given fileglob pattern
    """

    pattern: AnyStr

    def __call__(self, entry: os.DirEntry[AnyStr]) -> bool:
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
SELECT_VCS_FILES = SelectNames(
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
) | SelectGlob("?*,v")

#: .. versionadded:: 0.3.0
#:
#: Selects `~os.DirEntry`'s matched by either `SELECT_VCS_DIRS` or
#: `SELECT_VCS_FILES`
SELECT_VCS = SELECT_VCS_DIRS | SELECT_VCS_FILES
